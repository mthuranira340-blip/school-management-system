from io import BytesIO
from datetime import datetime

from flask import Blueprint, abort, flash, make_response, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy import or_

from ..extensions import db
from ..forms import (
    AchievementForm,
    ActivityForm,
    AdmissionForm,
    FeeStructureForm,
    FinanceReportForm,
    HealthRecordForm,
    MessageForm,
    ParentCommentForm,
    PaymentForm,
    ResultForm,
    StudentForm,
    SubjectForm,
)
from ..models import (
    Achievement,
    Activity,
    FeePayment,
    FeeStructure,
    FinanceReport,
    HealthRecord,
    Message,
    ParentComment,
    ParentStudentLink,
    Result,
    Student,
    Subject,
    User,
)
from ..services import dashboard_counts, fee_snapshot, generate_school_email, generate_student_portal_id, overall_performance, performance_trend, result_payload, student_result_cards, subject_breakdown


main_bp = Blueprint("main", __name__)


def require_roles(*roles):
    if current_user.role not in roles:
        abort(403)


def parent_students():
    return [link.linked_student for link in current_user.linked_students]


def visible_students():
    if current_user.role in {"admin", "teacher"}:
        return Student.query.order_by(Student.class_name.asc(), Student.first_name.asc()).all()
    return parent_students()


def selected_student():
    students = visible_students()
    if not students:
        return None

    requested_id = request.args.get("student_id", type=int)
    if requested_id:
        for student in students:
            if student.id == requested_id:
                return student
    return students[0]


def student_parent_contacts(student):
    if not student:
        return []
    parent_ids = [link.parent_id for link in student.parents]
    if not parent_ids:
        return []
    return User.query.filter(User.id.in_(parent_ids)).order_by(User.full_name.asc()).all()


def can_view_student(student):
    if current_user.role in {"admin", "teacher", "finance"}:
        return True
    return student in parent_students()


def populate_student_choices(*forms):
    students = Student.query.order_by(Student.first_name.asc(), Student.last_name.asc()).all()
    choices = [(student.id, f"{student.full_name} ({student.admission_number})") for student in students]
    for form in forms:
        if hasattr(form, "student_id"):
            form.student_id.choices = choices


def populate_subject_choices(form):
    subjects = Subject.query.order_by(Subject.name.asc()).all()
    form.subject_id.choices = [(subject.id, f"{subject.code} - {subject.name}") for subject in subjects]


def populate_parent_choices(form):
    parents = User.query.filter_by(role="parent").order_by(User.full_name.asc()).all()
    form.parent_id.choices = [(0, "No parent account")] + [(parent.id, f"{parent.full_name} ({parent.school_email})") for parent in parents]


def populate_payment_fee_choices(form):
    student_id = form.student_id.data or request.form.get("student_id", type=int)
    records = FeeStructure.query.order_by(FeeStructure.academic_year.desc(), FeeStructure.term.desc()).all()
    if student_id:
        records = [record for record in records if record.student_id == student_id]
    form.fee_structure_id.choices = [(record.id, f"{record.student.full_name} - {record.term} {record.academic_year}") for record in records]


def populate_message_choices(form):
    receivers = User.query.filter(User.id != current_user.id).order_by(User.full_name.asc()).all()
    form.receiver_id.choices = [(user.id, f"{user.full_name} ({user.role.title()})") for user in receivers]
    students = visible_students() if current_user.is_parent else Student.query.order_by(Student.first_name.asc()).all()
    form.student_id.choices = [(0, "No student selected")] + [(student.id, student.full_name) for student in students]


def populate_comment_student_choices(form):
    if current_user.role == "parent":
        students = parent_students()
    else:
        students = Student.query.order_by(Student.first_name.asc()).all()
    form.student_id.choices = [(0, "General school feedback")] + [(student.id, student.full_name) for student in students]


@main_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return redirect(url_for("auth.login"))


@main_bp.route("/dashboard")
@login_required
def dashboard():
    student = selected_student()
    students = visible_students()
    counts = dashboard_counts()
    recent_messages = (
        Message.query.filter_by(receiver_id=current_user.id)
        .order_by(Message.sent_at.desc())
        .limit(5)
        .all()
    )

    performance = overall_performance(student) if student else None
    result_cards = student_result_cards(student)[:5] if student else []
    trend_labels, trend_values = performance_trend(student) if student else ([], [])
    subject_labels, subject_values = subject_breakdown(student) if student else ([], [])
    fees = fee_snapshot(student) if student else None

    low_grade_alerts = [card for card in result_cards if card["grade"] in {"D", "E"}]
    upcoming_activities = sorted(student.activities, key=lambda item: item.created_at, reverse=True)[:4] if student else []
    latest_achievements = sorted(student.achievements, key=lambda item: item.achievement_date, reverse=True)[:4] if student else []
    parent_contacts = student_parent_contacts(student)
    health_records = (
        HealthRecord.query.filter_by(student_id=student.id).order_by(HealthRecord.created_at.desc()).limit(4).all()
        if student
        else []
    )
    recent_comments = ParentComment.query.order_by(ParentComment.created_at.desc()).limit(4).all() if current_user.role in {"admin", "teacher"} else []
    finance_reports = []
    if current_user.role == "finance":
        finance_reports = FinanceReport.query.filter_by(submitted_by_id=current_user.id).order_by(FinanceReport.submitted_at.desc()).limit(5).all()
    elif current_user.role in {"admin", "teacher"}:
        query = FinanceReport.query.order_by(FinanceReport.submitted_at.desc())
        if current_user.role == "teacher":
            query = query.filter_by(teacher_shared=True)
        finance_reports = query.limit(5).all()

    return render_template(
        "dashboard.html",
        counts=counts,
        student=student,
        students=students,
        performance=performance,
        result_cards=result_cards,
        trend_labels=trend_labels,
        trend_values=trend_values,
        subject_labels=subject_labels,
        subject_values=subject_values,
        fees=fees,
        low_grade_alerts=low_grade_alerts,
        upcoming_activities=upcoming_activities,
        latest_achievements=latest_achievements,
        health_records=health_records,
        recent_comments=recent_comments,
        finance_reports=finance_reports,
        parent_contacts=parent_contacts,
        recent_messages=recent_messages,
    )


@main_bp.route("/students", methods=["GET", "POST"])
@login_required
def students():
    require_roles("admin", "teacher")
    form = StudentForm()
    populate_parent_choices(form)

    if form.validate_on_submit():
        student = Student(
            first_name=form.first_name.data.strip(),
            last_name=form.last_name.data.strip(),
            admission_number=form.admission_number.data.strip().upper(),
            portal_student_id=generate_student_portal_id(form.admission_number.data.strip().upper()),
            class_name=form.class_name.data,
            stream=form.stream.data,
            profile_photo=form.profile_photo.data.strip() if form.profile_photo.data else "",
            school_email=generate_school_email(form.admission_number.data.strip().upper()),
        )
        db.session.add(student)
        db.session.flush()

        if form.parent_id.data:
            db.session.add(ParentStudentLink(parent_id=form.parent_id.data, student_id=student.id))

        db.session.commit()
        flash(f"Student profile created successfully. Portal ID: {student.portal_student_id}", "success")
        return redirect(url_for("main.students"))

    query = request.args.get("q", "").strip()
    students_query = Student.query
    if query:
        like = f"%{query}%"
        students_query = students_query.filter(
            or_(
                Student.first_name.ilike(like),
                Student.last_name.ilike(like),
                Student.admission_number.ilike(like),
                Student.class_name.ilike(like),
                Student.stream.ilike(like),
            )
        )

    student_list = students_query.order_by(Student.class_name.asc(), Student.first_name.asc()).all()
    return render_template("students.html", form=form, student_list=student_list, query=query)


@main_bp.route("/students/<int:student_id>")
@login_required
def student_profile(student_id):
    student = db.session.get(Student, student_id)
    if not student:
        abort(404)
    if not can_view_student(student):
        abort(403)

    results = student_result_cards(student)
    performance = overall_performance(student)
    trend_labels, trend_values = performance_trend(student)
    subject_labels, subject_values = subject_breakdown(student)
    fee_data = fee_snapshot(student)
    payments = sorted(student.fee_payments, key=lambda item: item.payment_date, reverse=True)
    parent_contacts = student_parent_contacts(student)
    health_records = HealthRecord.query.filter_by(student_id=student.id).order_by(HealthRecord.created_at.desc()).all()
    student_comments = ParentComment.query.filter(
        or_(ParentComment.student_id == student.id, ParentComment.student_id.is_(None))
    ).order_by(ParentComment.created_at.desc()).all()

    return render_template(
        "student_profile.html",
        student=student,
        results=results,
        performance=performance,
        trend_labels=trend_labels,
        trend_values=trend_values,
        subject_labels=subject_labels,
        subject_values=subject_values,
        fee_data=fee_data,
        payments=payments,
        health_records=health_records,
        student_comments=student_comments,
        parent_contacts=parent_contacts,
    )


@main_bp.route("/academics", methods=["GET", "POST"])
@login_required
def academics():
    require_roles("admin", "teacher")
    subject_form = SubjectForm(prefix="subject")
    result_form = ResultForm(prefix="result")
    activity_form = ActivityForm(prefix="activity")
    achievement_form = AchievementForm(prefix="achievement")

    populate_student_choices(result_form, activity_form, achievement_form)
    populate_subject_choices(result_form)

    if subject_form.submit.data and subject_form.validate_on_submit():
        subject = Subject(name=subject_form.name.data.strip(), code=subject_form.code.data.strip().upper())
        db.session.add(subject)
        db.session.commit()
        flash("Subject saved successfully.", "success")
        return redirect(url_for("main.academics"))

    if result_form.submit.data and result_form.validate_on_submit():
        result = Result(
            student_id=result_form.student_id.data,
            subject_id=result_form.subject_id.data,
            term=result_form.term.data,
            academic_year=result_form.academic_year.data.strip(),
            cat_score=float(result_form.cat_score.data),
            exam_score=float(result_form.exam_score.data),
            created_by_id=current_user.id,
        )
        db.session.add(result)
        db.session.commit()
        flash("Result recorded successfully.", "success")
        return redirect(url_for("main.academics"))

    if activity_form.submit.data and activity_form.validate_on_submit():
        activity = Activity(
            student_id=activity_form.student_id.data,
            activity_name=activity_form.activity_name.data.strip(),
            activity_type=activity_form.activity_type.data,
            participation_level=activity_form.participation_level.data,
            progress_percent=activity_form.progress_percent.data,
            progress_note=activity_form.progress_note.data.strip() if activity_form.progress_note.data else "",
        )
        db.session.add(activity)
        db.session.commit()
        flash("Activity progress saved successfully.", "success")
        return redirect(url_for("main.academics"))

    if achievement_form.submit.data and achievement_form.validate_on_submit():
        achievement = Achievement(
            student_id=achievement_form.student_id.data,
            title=achievement_form.title.data.strip(),
            category=achievement_form.category.data.strip(),
            description=achievement_form.description.data.strip(),
            achievement_date=achievement_form.achievement_date.data,
        )
        db.session.add(achievement)
        db.session.commit()
        flash("Achievement saved successfully.", "success")
        return redirect(url_for("main.academics"))

    result_rows = [result_payload(entry) for entry in Result.query.order_by(Result.created_at.desc()).limit(12).all()]
    subjects = Subject.query.order_by(Subject.name.asc()).all()
    recent_activities = Activity.query.order_by(Activity.created_at.desc()).limit(8).all()
    recent_achievements = Achievement.query.order_by(Achievement.achievement_date.desc()).limit(8).all()

    return render_template(
        "academics.html",
        subject_form=subject_form,
        result_form=result_form,
        activity_form=activity_form,
        achievement_form=achievement_form,
        result_rows=result_rows,
        subjects=subjects,
        recent_activities=recent_activities,
        recent_achievements=recent_achievements,
    )


@main_bp.route("/fees", methods=["GET", "POST"])
@login_required
def fees():
    structure_form = FeeStructureForm(prefix="structure")
    payment_form = PaymentForm(prefix="payment")

    populate_student_choices(structure_form, payment_form)
    populate_payment_fee_choices(payment_form)

    if current_user.role in {"admin", "teacher"}:
        if structure_form.submit.data and structure_form.validate_on_submit():
            fee = FeeStructure(
                student_id=structure_form.student_id.data,
                term=structure_form.term.data,
                academic_year=structure_form.academic_year.data.strip(),
                total_amount=structure_form.total_amount.data,
                due_date=structure_form.due_date.data,
            )
            db.session.add(fee)
            db.session.commit()
            flash("Fee structure saved successfully.", "success")
            return redirect(url_for("main.fees"))

        if payment_form.submit.data and payment_form.validate_on_submit():
            payment = FeePayment(
                student_id=payment_form.student_id.data,
                fee_structure_id=payment_form.fee_structure_id.data,
                amount_paid=payment_form.amount_paid.data,
                payment_date=payment_form.payment_date.data,
                reference=payment_form.reference.data.strip(),
                recorded_by=current_user.full_name,
            )
            db.session.add(payment)
            db.session.commit()
            flash("Payment recorded successfully.", "success")
            return redirect(url_for("main.fees"))
    else:
        structure_form = None
        payment_form = None

    records = visible_students() if current_user.role == "parent" else Student.query.order_by(Student.first_name.asc()).all()
    fee_cards = [{"student": student, "snapshot": fee_snapshot(student), "latest_fee": student.latest_fee} for student in records]
    recent_payments_query = FeePayment.query.order_by(FeePayment.payment_date.desc())
    if current_user.role == "parent":
        allowed_ids = [student.id for student in records]
        recent_payments_query = recent_payments_query.filter(FeePayment.student_id.in_(allowed_ids or [0]))
    recent_payments = recent_payments_query.limit(12).all()

    return render_template(
        "fees.html",
        structure_form=structure_form,
        payment_form=payment_form,
        fee_cards=fee_cards,
        recent_payments=recent_payments,
    )


@main_bp.route("/messages", methods=["GET", "POST"])
@login_required
def messages():
    form = MessageForm()
    populate_message_choices(form)

    if form.validate_on_submit():
        student_id = form.student_id.data or None
        if current_user.role == "parent" and student_id:
            permitted_ids = {student.id for student in parent_students()}
            if student_id not in permitted_ids:
                abort(403)

        message = Message(
            sender_id=current_user.id,
            receiver_id=form.receiver_id.data,
            student_id=student_id,
            category=form.category.data,
            subject=form.subject.data.strip(),
            body=form.body.data.strip(),
        )
        db.session.add(message)
        db.session.commit()
        flash("Notification sent successfully.", "success")
        return redirect(url_for("main.messages"))

    inbox = Message.query.filter_by(receiver_id=current_user.id).order_by(Message.sent_at.desc()).all()
    sent = Message.query.filter_by(sender_id=current_user.id).order_by(Message.sent_at.desc()).limit(8).all()
    return render_template("messages.html", form=form, inbox=inbox, sent=sent)


@main_bp.route("/health", methods=["GET", "POST"])
@login_required
def health():
    require_roles("admin", "teacher")
    form = HealthRecordForm()
    populate_student_choices(form)

    if form.validate_on_submit():
        record = HealthRecord(
            student_id=form.student_id.data,
            term=form.term.data,
            academic_year=form.academic_year.data.strip(),
            treatment=form.treatment.data.strip(),
            notes=form.notes.data.strip() if form.notes.data else "",
            recorded_by_id=current_user.id,
        )
        db.session.add(record)
        db.session.commit()
        flash("Health status saved successfully.", "success")
        return redirect(url_for("main.health"))

    records = HealthRecord.query.order_by(HealthRecord.created_at.desc()).limit(30).all()
    return render_template("health.html", form=form, records=records)


@main_bp.route("/comments", methods=["GET", "POST"])
@login_required
def comments():
    form = ParentCommentForm()
    populate_comment_student_choices(form)

    if form.validate_on_submit():
        if current_user.role != "parent":
            abort(403)
        student_id = form.student_id.data or None
        if student_id:
            allowed = {student.id for student in parent_students()}
            if student_id not in allowed:
                abort(403)
        comment = ParentComment(
            parent_id=current_user.id,
            student_id=student_id,
            category=form.category.data,
            comment=form.comment.data.strip(),
        )
        db.session.add(comment)
        db.session.commit()
        flash("Comment posted successfully.", "success")
        return redirect(url_for("main.comments"))

    if current_user.role == "parent":
        comments_list = ParentComment.query.filter_by(parent_id=current_user.id).order_by(ParentComment.created_at.desc()).all()
    else:
        comments_list = ParentComment.query.order_by(ParentComment.created_at.desc()).all()
    return render_template("comments.html", form=form, comments_list=comments_list)


@main_bp.route("/admissions", methods=["GET", "POST"])
@login_required
def admissions():
    require_roles("admin", "teacher")
    form = AdmissionForm()
    populate_parent_choices(form)

    if form.validate_on_submit():
        admission_number = form.admission_number.data.strip().upper()
        student = Student(
            first_name=form.first_name.data.strip(),
            last_name=form.last_name.data.strip(),
            admission_number=admission_number,
            portal_student_id=generate_student_portal_id(admission_number),
            class_name=form.class_name.data,
            stream=form.stream.data,
            profile_photo=form.profile_photo.data.strip() if form.profile_photo.data else "",
            school_email=generate_school_email(admission_number),
        )
        db.session.add(student)
        db.session.flush()

        if form.parent_id.data:
            db.session.add(ParentStudentLink(parent_id=form.parent_id.data, student_id=student.id))

        db.session.commit()
        flash(f"New student admitted successfully. Portal ID: {student.portal_student_id}", "success")
        return redirect(url_for("main.admissions"))

    recent_admissions = Student.query.order_by(Student.created_at.desc()).limit(20).all()
    return render_template("admissions.html", form=form, recent_admissions=recent_admissions)


@main_bp.route("/finance", methods=["GET", "POST"])
@login_required
def finance():
    form = FinanceReportForm()

    if current_user.role == "finance":
        if form.validate_on_submit():
            report = FinanceReport(
                submitted_by_id=current_user.id,
                term=form.term.data,
                academic_year=form.academic_year.data.strip(),
                title=form.title.data.strip(),
                amount_collected=form.amount_collected.data,
                expected_amount=form.expected_amount.data,
                report_body=form.report_body.data.strip(),
            )
            db.session.add(report)
            db.session.commit()
            flash("Finance report sent to the principal.", "success")
            return redirect(url_for("main.finance"))
        reports = FinanceReport.query.filter_by(submitted_by_id=current_user.id).order_by(FinanceReport.submitted_at.desc()).all()
        return render_template("finance.html", form=form, reports=reports, mode="finance")

    if current_user.role == "admin":
        action = request.args.get("action")
        report_id = request.args.get("report_id", type=int)
        if action == "share" and report_id:
            report = db.session.get(FinanceReport, report_id)
            if report:
                report.teacher_shared = True
                report.reviewed_by_admin_id = current_user.id
                report.reviewed_at = datetime.utcnow()
                db.session.commit()
                teacher_ids = [teacher.id for teacher in User.query.filter_by(role="teacher").all()]
                for teacher_id in teacher_ids:
                    db.session.add(
                        Message(
                            sender_id=current_user.id,
                            receiver_id=teacher_id,
                            category="Finance",
                            subject=f"Finance report shared: {report.title}",
                            body=f"Finance report for {report.term} {report.academic_year} has been approved by the principal and shared with staff.",
                        )
                    )
                db.session.commit()
                flash("Finance report shared with teachers.", "success")
            return redirect(url_for("main.finance"))

        reports = FinanceReport.query.order_by(FinanceReport.submitted_at.desc()).all()
        return render_template("finance.html", form=None, reports=reports, mode="admin")

    if current_user.role == "teacher":
        reports = FinanceReport.query.filter_by(teacher_shared=True).order_by(FinanceReport.submitted_at.desc()).all()
        return render_template("finance.html", form=None, reports=reports, mode="teacher")

    abort(403)


@main_bp.route("/export/pdf/<int:student_id>")
@login_required
def export_pdf(student_id):
    student = db.session.get(Student, student_id)
    if not student:
        abort(404)
    if current_user.role == "parent" and student not in parent_students():
        abort(403)

    results = student_result_cards(student)
    performance = overall_performance(student)
    fee_data = fee_snapshot(student)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()

    content = [
        Paragraph("Greenfield High School Report Card", styles["Title"]),
        Spacer(1, 12),
        Paragraph(f"Student: {student.full_name}", styles["Normal"]),
        Paragraph(f"Admission Number: {student.admission_number}", styles["Normal"]),
        Paragraph(f"Class: {student.class_name} {student.stream}", styles["Normal"]),
        Paragraph(f"Overall Grade: {performance['grade']} ({performance['status_label']})", styles["Normal"]),
        Paragraph(f"Average Score: {performance['average']}", styles["Normal"]),
        Paragraph(f"GPA: {performance['gpa']}", styles["Normal"]),
        Paragraph(f"Fees Status: {fee_data['status']} | Balance: KES {fee_data['balance']}", styles["Normal"]),
        Spacer(1, 12),
    ]

    table_data = [["Subject", "Term", "CAT", "Exam", "Total", "Grade"]]
    for result in results:
        table_data.append([result["subject"], result["term"], result["cat_score"], result["exam_score"], result["total_score"], result["grade"]])

    table = Table(table_data, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4c73")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.HexColor("#e9f2f8")]),
            ]
        )
    )
    content.append(table)
    doc.build(content)
    buffer.seek(0)

    response = make_response(buffer.getvalue())
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"attachment; filename={student.admission_number.lower()}_report_card.pdf"
    return response
