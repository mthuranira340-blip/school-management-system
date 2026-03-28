from datetime import datetime
from decimal import Decimal

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db, login_manager


class ParentStudentLink(db.Model):
    __tablename__ = "parent_student_links"

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    school_email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(30), nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    linked_students = db.relationship(
        "ParentStudentLink",
        foreign_keys=[ParentStudentLink.parent_id],
        backref="parent",
        lazy=True,
        cascade="all, delete-orphan",
    )
    created_results = db.relationship("Result", backref="recorded_by", lazy=True, foreign_keys="Result.created_by_id")
    sent_messages = db.relationship("Message", backref="sender", lazy=True, foreign_keys="Message.sender_id")
    received_messages = db.relationship("Message", backref="receiver", lazy=True, foreign_keys="Message.receiver_id")

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    @property
    def password(self):
        raise AttributeError("Password is write-only.")

    @property
    def is_admin(self):
        return self.role == "admin"

    @property
    def is_teacher(self):
        return self.role == "teacher"

    @property
    def is_parent(self):
        return self.role == "parent"


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    admission_number = db.Column(db.String(30), unique=True, nullable=False)
    portal_student_id = db.Column(db.String(40), unique=True, nullable=False)
    class_name = db.Column(db.String(40), nullable=False)
    stream = db.Column(db.String(40), nullable=False)
    profile_photo = db.Column(db.String(255), nullable=True)
    school_email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    results = db.relationship("Result", backref="student", lazy=True, cascade="all, delete-orphan")
    activities = db.relationship("Activity", backref="student", lazy=True, cascade="all, delete-orphan")
    achievements = db.relationship("Achievement", backref="student", lazy=True, cascade="all, delete-orphan")
    fee_structures = db.relationship("FeeStructure", backref="student", lazy=True, cascade="all, delete-orphan")
    fee_payments = db.relationship("FeePayment", backref="student", lazy=True, cascade="all, delete-orphan")
    parents = db.relationship(
        "ParentStudentLink",
        foreign_keys=[ParentStudentLink.student_id],
        backref="linked_student",
        lazy=True,
        cascade="all, delete-orphan",
    )
    messages = db.relationship("Message", backref="student_profile", lazy=True, cascade="all, delete-orphan")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def initials(self):
        return f"{self.first_name[:1]}{self.last_name[:1]}".upper()

    @property
    def latest_fee(self):
        if not self.fee_structures:
            return None
        return sorted(self.fee_structures, key=lambda item: (item.academic_year, item.term), reverse=True)[0]


class Subject(db.Model):
    __tablename__ = "subjects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)

    results = db.relationship("Result", backref="subject", lazy=True, cascade="all, delete-orphan")


class Result(db.Model):
    __tablename__ = "results"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=False)
    term = db.Column(db.String(30), nullable=False)
    academic_year = db.Column(db.String(20), nullable=False)
    cat_score = db.Column(db.Float, nullable=False, default=0)
    exam_score = db.Column(db.Float, nullable=False, default=0)
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    @property
    def total_score(self):
        return round((self.cat_score or 0) + (self.exam_score or 0), 2)

    @property
    def average_score(self):
        return round(self.total_score / 2, 2)


class Activity(db.Model):
    __tablename__ = "activities"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    activity_name = db.Column(db.String(120), nullable=False)
    activity_type = db.Column(db.String(40), nullable=False)
    participation_level = db.Column(db.String(40), nullable=False)
    progress_note = db.Column(db.Text, nullable=True)
    progress_percent = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Achievement(db.Model):
    __tablename__ = "achievements"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(40), nullable=False)
    description = db.Column(db.Text, nullable=False)
    achievement_date = db.Column(db.Date, nullable=False)


class FeeStructure(db.Model):
    __tablename__ = "fee_structures"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    term = db.Column(db.String(30), nullable=False)
    academic_year = db.Column(db.String(20), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    due_date = db.Column(db.Date, nullable=False)

    payments = db.relationship("FeePayment", backref="fee_structure", lazy=True, cascade="all, delete-orphan")

    @property
    def paid_amount(self):
        return round(sum((payment.amount_paid or Decimal("0")) for payment in self.payments), 2)

    @property
    def balance(self):
        return round(float(self.total_amount) - float(self.paid_amount), 2)


class FeePayment(db.Model):
    __tablename__ = "fee_payments"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    fee_structure_id = db.Column(db.Integer, db.ForeignKey("fee_structures.id"), nullable=False)
    amount_paid = db.Column(db.Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    reference = db.Column(db.String(80), nullable=False)
    recorded_by = db.Column(db.String(80), nullable=False)


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=True)
    category = db.Column(db.String(40), nullable=False)
    subject = db.Column(db.String(120), nullable=False)
    body = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
