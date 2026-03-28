from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_user, logout_user
from sqlalchemy import func

from ..extensions import db
from ..forms import LoginForm, ParentPortalLoginForm, RegistrationForm
from ..models import ParentStudentLink, Student, User
from ..services import generate_school_email


auth_bp = Blueprint("auth", __name__)


def populate_linked_students(form):
    students = Student.query.order_by(Student.first_name.asc(), Student.last_name.asc()).all()
    form.linked_student_id.choices = [(0, "Select student")] + [(student.id, f"{student.full_name} ({student.admission_number})") for student in students]


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = RegistrationForm()
    populate_linked_students(form)

    if form.validate_on_submit():
        user = User(
            full_name=form.full_name.data.strip(),
            username=form.username.data.strip().lower(),
            email=form.email.data.strip().lower(),
            school_email=generate_school_email(form.username.data.strip().lower()),
            phone_number=form.phone_number.data.strip() if form.phone_number.data else "",
            gender=form.gender.data or "",
            role=form.role.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()

        if user.is_parent and form.linked_student_id.data:
            db.session.add(ParentStudentLink(parent_id=user.id, student_id=form.linked_student_id.data))

        db.session.commit()
        flash("Account created successfully. Use your personal email and password to sign in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm(prefix="account")
    parent_portal_form = ParentPortalLoginForm(prefix="parent_portal")

    if form.submit.data and form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash(f"Welcome back, {user.full_name}.", "success")
            return redirect(url_for("main.dashboard"))
        flash("Invalid email or password.", "danger")

    if parent_portal_form.submit.data and parent_portal_form.validate_on_submit():
        student_name = parent_portal_form.student_name.data.strip().lower()
        portal_student_id = parent_portal_form.portal_student_id.data.strip().upper()
        student = Student.query.filter(
            func.lower(Student.first_name + " " + Student.last_name) == student_name,
            Student.portal_student_id == portal_student_id,
        ).first()

        if student:
            link = ParentStudentLink.query.filter_by(student_id=student.id).first()
            if link:
                parent = db.session.get(User, link.parent_id)
                if parent:
                    login_user(parent)
                    flash(f"Welcome to {student.full_name}'s parent portal.", "success")
                    return redirect(url_for("main.dashboard", student_id=student.id))

        flash("Student name or portal ID is incorrect.", "danger")

    return render_template("login.html", form=form, parent_portal_form=parent_portal_form)


@auth_bp.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
