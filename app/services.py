from collections import defaultdict
from datetime import date
from decimal import Decimal

from sqlalchemy import inspect, text

from .extensions import db
from .models import Achievement, Activity, FeePayment, FeeStructure, FinanceReport, HealthRecord, Message, ParentComment, ParentStudentLink, Result, Student, Subject, User


GRADE_RULES = [
    (80, "A", 4.0, "Excellent", "🟢"),
    (70, "B", 3.0, "Good", "🟡"),
    (60, "C", 2.0, "Average", "🟡"),
    (50, "D", 1.0, "Needs Improvement", "🔴"),
    (0, "E", 0.0, "Needs Improvement", "🔴"),
]


def generate_school_email(identifier, domain="greenfieldhigh.edu"):
    return f"{str(identifier).strip().lower()}@{domain}"


def generate_student_portal_id(admission_number):
    return f"STU-{str(admission_number).strip().upper()}"


def score_to_grade(score):
    numeric_score = float(score or 0)
    for minimum, grade, points, label, icon in GRADE_RULES:
        if numeric_score >= minimum:
            return {"grade": grade, "points": points, "label": label, "icon": icon}
    return {"grade": "E", "points": 0.0, "label": "Needs Improvement", "icon": "🔴"}


def result_payload(result):
    grade_data = score_to_grade(result.total_score)
    return {
        "id": result.id,
        "subject": result.subject.name,
        "subject_code": result.subject.code,
        "term": result.term,
        "academic_year": result.academic_year,
        "cat_score": float(result.cat_score),
        "exam_score": float(result.exam_score),
        "total_score": result.total_score,
        "average_score": result.average_score,
        "grade": grade_data["grade"],
        "grade_points": grade_data["points"],
        "status_label": grade_data["label"],
        "status_icon": grade_data["icon"],
    }


def student_result_cards(student):
    return [result_payload(entry) for entry in sorted(student.results, key=lambda item: (item.academic_year, item.term, item.subject.code))]


def overall_performance(student):
    cards = student_result_cards(student)
    if not cards:
        return {
            "average": 0,
            "grade": "N/A",
            "gpa": 0,
            "status_label": "No results yet",
            "status_icon": "⚪",
        }

    average = round(sum(card["total_score"] for card in cards) / len(cards), 2)
    grade_data = score_to_grade(average)
    gpa = round(sum(card["grade_points"] for card in cards) / len(cards), 2)
    return {
        "average": average,
        "grade": grade_data["grade"],
        "gpa": gpa,
        "status_label": grade_data["label"],
        "status_icon": grade_data["icon"],
    }


def performance_trend(student):
    grouped = defaultdict(list)
    for item in student.results:
        grouped[f"{item.term} {item.academic_year}"].append(item.total_score)

    labels = list(grouped.keys())
    values = [round(sum(scores) / len(scores), 2) for scores in grouped.values()]
    return labels, values


def subject_breakdown(student):
    grouped = defaultdict(list)
    for item in student.results:
        grouped[item.subject.name].append(item.total_score)
    labels = list(grouped.keys())
    values = [round(sum(scores) / len(scores), 2) for scores in grouped.values()]
    return labels, values


def fee_snapshot(student):
    fee = student.latest_fee
    if not fee:
        return {
            "total": 0,
            "paid": 0,
            "balance": 0,
            "status": "Pending",
            "icon": "⚠️",
        }

    balance = fee.balance
    if balance <= 0:
        return {"total": float(fee.total_amount), "paid": float(fee.paid_amount), "balance": 0, "status": "Paid", "icon": "✅"}
    if fee.due_date < date.today():
        return {
            "total": float(fee.total_amount),
            "paid": float(fee.paid_amount),
            "balance": balance,
            "status": "Overdue",
            "icon": "❌",
        }
    return {
        "total": float(fee.total_amount),
        "paid": float(fee.paid_amount),
        "balance": balance,
        "status": "Pending",
        "icon": "⚠️",
    }


def dashboard_counts():
    return {
        "students": Student.query.count(),
        "subjects": Subject.query.count(),
        "parents": User.query.filter_by(role="parent").count(),
        "teachers": User.query.filter_by(role="teacher").count(),
    }


def ensure_schema_updates():
    inspector = inspect(db.engine)

    if "users" in inspector.get_table_names():
        user_columns = {column["name"] for column in inspector.get_columns("users")}
        if "phone_number" not in user_columns:
            db.session.execute(text("ALTER TABLE users ADD COLUMN phone_number VARCHAR(30)"))
        if "gender" not in user_columns:
            db.session.execute(text("ALTER TABLE users ADD COLUMN gender VARCHAR(20)"))

    if "students" in inspector.get_table_names():
        student_columns = {column["name"] for column in inspector.get_columns("students")}
        if "portal_student_id" not in student_columns:
            db.session.execute(text("ALTER TABLE students ADD COLUMN portal_student_id VARCHAR(40)"))
            students = Student.query.all()
            for student in students:
                student.portal_student_id = generate_student_portal_id(student.admission_number)
        else:
            students = Student.query.filter(
                (Student.portal_student_id.is_(None)) | (Student.portal_student_id == "")
            ).all()
            for student in students:
                student.portal_student_id = generate_student_portal_id(student.admission_number)

    db.session.commit()


def seed_demo_data():
    if User.query.first():
        finance = User.query.filter_by(role="finance").first()
        if not finance:
            finance = User(
                full_name="Finance Office",
                username="finance",
                email="finance@demo.local",
                school_email=generate_school_email("finance"),
                role="finance",
            )
            finance.set_password("finance123")
            db.session.add(finance)
            db.session.flush()

        student = Student.query.order_by(Student.id.asc()).first()
        parent = User.query.filter_by(role="parent").order_by(User.id.asc()).first()
        teacher = User.query.filter_by(role="teacher").order_by(User.id.asc()).first()

        if student and teacher and not HealthRecord.query.filter_by(student_id=student.id).first():
            db.session.add(
                HealthRecord(
                    student_id=student.id,
                    term="Term 1",
                    academic_year="2026",
                    treatment="Typhoid vaccination",
                    notes="Follow-up review completed and student cleared for classes.",
                    recorded_by_id=teacher.id,
                )
            )

        if student and parent and not ParentComment.query.filter_by(parent_id=parent.id).first():
            db.session.add(
                ParentComment(
                    parent_id=parent.id,
                    student_id=student.id,
                    category="Performance",
                    comment="Amina has improved well in Mathematics. Please keep the revision support sessions active.",
                )
            )

        if finance and not FinanceReport.query.filter_by(submitted_by_id=finance.id).first():
            db.session.add(
                FinanceReport(
                    submitted_by_id=finance.id,
                    term="Term 1",
                    academic_year="2026",
                    title="Fee Collection Progress",
                    amount_collected=Decimal("1200000.00"),
                    expected_amount=Decimal("1500000.00"),
                    report_body="Collection is at 80 percent. Priority follow-up is ongoing for balances over 30 days.",
                    teacher_shared=False,
                )
            )

        db.session.commit()
        return

    admin = User(
        full_name="Grace Wanjiru",
        username="admin",
        email="admin@demo.local",
        school_email=generate_school_email("admin"),
        role="admin",
    )
    admin.set_password("admin123")

    teacher = User(
        full_name="Mr. Otieno",
        username="teacher",
        email="teacher@demo.local",
        school_email=generate_school_email("teacher"),
        role="teacher",
    )
    teacher.set_password("teacher123")

    finance = User(
        full_name="Finance Office",
        username="finance",
        email="finance@demo.local",
        school_email=generate_school_email("finance"),
        role="finance",
    )
    finance.set_password("finance123")

    parent = User(
        full_name="Sarah Njeri",
        username="parent",
        email="parent@demo.local",
        school_email=generate_school_email("parent"),
        phone_number="+254700123456",
        gender="Female",
        role="parent",
    )
    parent.set_password("parent123")

    db.session.add_all([admin, teacher, parent, finance])
    db.session.flush()

    student = Student(
        first_name="Amina",
        last_name="Kamau",
        admission_number="ADM001",
        portal_student_id=generate_student_portal_id("ADM001"),
        class_name="Form 3",
        stream="North",
        profile_photo="https://images.unsplash.com/photo-1544717305-2782549b5136?auto=format&fit=crop&w=400&q=80",
        school_email=generate_school_email("adm001"),
    )
    db.session.add(student)
    db.session.flush()

    db.session.add(ParentStudentLink(parent_id=parent.id, student_id=student.id))

    subjects = [
        Subject(name="Mathematics", code="MATH"),
        Subject(name="English", code="ENG"),
        Subject(name="Biology", code="BIO"),
        Subject(name="History", code="HIST"),
    ]
    db.session.add_all(subjects)
    db.session.flush()

    results = [
        Result(student_id=student.id, subject_id=subjects[0].id, term="Term 1", academic_year="2026", cat_score=34, exam_score=51, created_by_id=teacher.id),
        Result(student_id=student.id, subject_id=subjects[1].id, term="Term 1", academic_year="2026", cat_score=29, exam_score=39, created_by_id=teacher.id),
        Result(student_id=student.id, subject_id=subjects[2].id, term="Term 2", academic_year="2026", cat_score=32, exam_score=45, created_by_id=teacher.id),
        Result(student_id=student.id, subject_id=subjects[3].id, term="Term 2", academic_year="2026", cat_score=26, exam_score=31, created_by_id=teacher.id),
    ]
    db.session.add_all(results)

    db.session.add_all(
        [
            Activity(student_id=student.id, activity_name="Football Team", activity_type="Sports", participation_level="Excellent", progress_percent=86, progress_note="Selected for inter-school tournament."),
            Activity(student_id=student.id, activity_name="Science Club", activity_type="Club", participation_level="Active", progress_percent=72, progress_note="Leading the water filtration project."),
        ]
    )

    db.session.add_all(
        [
            Achievement(student_id=student.id, title="Top 10 Mathematics", category="Academic Award", description="Ranked in the top ten school-wide in mathematics.", achievement_date=date(2026, 2, 14)),
            Achievement(student_id=student.id, title="Regional Football Silver Medal", category="Sports", description="Won silver at the regional girls football finals.", achievement_date=date(2026, 3, 5)),
        ]
    )

    fee = FeeStructure(
        student_id=student.id,
        term="Term 1",
        academic_year="2026",
        total_amount=Decimal("18500.00"),
        due_date=date(2026, 4, 15),
    )
    db.session.add(fee)
    db.session.flush()

    db.session.add(
        FeePayment(
            student_id=student.id,
            fee_structure_id=fee.id,
            amount_paid=Decimal("12000.00"),
            payment_date=date(2026, 2, 1),
            reference="RCPT-2026-001",
            recorded_by=teacher.full_name,
        )
    )

    db.session.add_all(
        [
            Message(sender_id=admin.id, receiver_id=parent.id, student_id=student.id, category="Weekend Travel", subject="Weekend travel notice", body="Students will be released on Friday at 3:00 PM and should return by Sunday 5:00 PM."),
            Message(sender_id=teacher.id, receiver_id=parent.id, student_id=student.id, category="Co-Curricular", subject="Football training camp", body="Amina has been selected for the Saturday morning football training camp."),
            Message(sender_id=teacher.id, receiver_id=parent.id, student_id=student.id, category="Academic", subject="Mid-term performance update", body="Amina is showing strong progress in Mathematics and Biology. Please encourage revision in History."),
        ]
    )

    db.session.add(
        HealthRecord(
            student_id=student.id,
            term="Term 1",
            academic_year="2026",
            treatment="Typhoid vaccination",
            notes="Follow-up review completed and student cleared for classes.",
            recorded_by_id=teacher.id,
        )
    )

    db.session.add(
        ParentComment(
            parent_id=parent.id,
            student_id=student.id,
            category="Performance",
            comment="Amina has improved well in Mathematics. Please keep the revision support sessions active.",
        )
    )

    db.session.add(
        FinanceReport(
            submitted_by_id=finance.id,
            term="Term 1",
            academic_year="2026",
            title="Fee Collection Progress",
            amount_collected=Decimal("1200000.00"),
            expected_amount=Decimal("1500000.00"),
            report_body="Collection is at 80 percent. Priority follow-up is ongoing for balances over 30 days.",
            teacher_shared=False,
        )
    )

    db.session.commit()
