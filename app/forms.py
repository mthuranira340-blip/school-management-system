from flask_wtf import FlaskForm
from wtforms import DateField, DecimalField, IntegerField, PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional, ValidationError

from .models import Student, Subject, User


ROLE_CHOICES = [("admin", "Admin"), ("teacher", "Teacher"), ("parent", "Parent"), ("finance", "Finance")]
TERM_CHOICES = [("Term 1", "Term 1"), ("Term 2", "Term 2"), ("Term 3", "Term 3")]
CLASS_CHOICES = [(f"Form {level}", f"Form {level}") for level in range(1, 5)]
STREAM_CHOICES = [("North", "North"), ("South", "South"), ("East", "East"), ("West", "West")]
ACTIVITY_TYPES = [("Sports", "Sports"), ("Club", "Club"), ("Event", "Event")]
PARTICIPATION_LEVELS = [("Beginner", "Beginner"), ("Active", "Active"), ("Excellent", "Excellent")]
MESSAGE_CATEGORIES = [
    ("Announcement", "Announcement"),
    ("Weekend Travel", "Weekend Travel"),
    ("Co-Curricular", "Co-Curricular"),
    ("Fees", "Fees"),
    ("Academic", "Academic"),
]
COMMENT_CATEGORIES = [("Performance", "Performance"), ("School Development", "School Development")]


class RegistrationForm(FlaskForm):
    full_name = StringField("Full name", validators=[DataRequired(), Length(min=3, max=120)])
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField("Personal email", validators=[DataRequired(), Email()])
    phone_number = StringField("Phone number", validators=[Optional(), Length(max=30)])
    gender = SelectField(
        "Gender",
        choices=[("", "Select gender"), ("Female", "Female"), ("Male", "Male"), ("Other", "Other")],
        validators=[Optional()],
    )
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=128)])
    confirm_password = PasswordField(
        "Confirm password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")],
    )
    role = SelectField("Role", choices=ROLE_CHOICES, validators=[DataRequired()])
    linked_student_id = SelectField("Linked student", coerce=int, choices=[], validators=[Optional()])
    submit = SubmitField("Create account")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.strip().lower()).first():
            raise ValidationError("That email is already registered.")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data.strip().lower()).first():
            raise ValidationError("That username is already taken.")

    def validate_linked_student_id(self, field):
        if self.role.data == "parent" and field.data == 0:
            raise ValidationError("Please link the parent account to a student.")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign in")


class ParentPortalLoginForm(FlaskForm):
    student_name = StringField("Student name", validators=[DataRequired(), Length(min=3, max=160)])
    portal_student_id = StringField("Student portal ID", validators=[DataRequired(), Length(min=4, max=40)])
    submit = SubmitField("Open parent portal")


class StudentForm(FlaskForm):
    first_name = StringField("First name", validators=[DataRequired(), Length(max=80)])
    last_name = StringField("Last name", validators=[DataRequired(), Length(max=80)])
    admission_number = StringField("Admission number", validators=[DataRequired(), Length(max=30)])
    class_name = SelectField("Class", choices=CLASS_CHOICES, validators=[DataRequired()])
    stream = SelectField("Stream", choices=STREAM_CHOICES, validators=[DataRequired()])
    profile_photo = StringField("Profile photo URL", validators=[Optional(), Length(max=255)])
    parent_id = SelectField("Parent account", coerce=int, choices=[], validators=[Optional()])
    submit = SubmitField("Save student")

    def __init__(self, original_admission=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_admission = original_admission

    def validate_admission_number(self, field):
        value = field.data.strip().upper()
        existing = Student.query.filter_by(admission_number=value).first()
        if existing and value != self.original_admission:
            raise ValidationError("That admission number already exists.")


class SubjectForm(FlaskForm):
    name = StringField("Subject name", validators=[DataRequired(), Length(max=80)])
    code = StringField("Subject code", validators=[DataRequired(), Length(max=20)])
    submit = SubmitField("Save subject")

    def __init__(self, original_code=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_code = original_code

    def validate_code(self, field):
        value = field.data.strip().upper()
        existing = Subject.query.filter_by(code=value).first()
        if existing and value != self.original_code:
            raise ValidationError("That subject code already exists.")


class StudentSubjectForm(FlaskForm):
    student_id = SelectField("Student", coerce=int, choices=[], validators=[DataRequired()])
    subject_id = SelectField("Subject", coerce=int, choices=[], validators=[DataRequired()])
    submit = SubmitField("Assign subject")


class ResultForm(FlaskForm):
    student_id = SelectField("Student", coerce=int, choices=[], validators=[DataRequired()])
    subject_id = SelectField("Subject", coerce=int, choices=[], validators=[DataRequired()])
    term = SelectField("Term", choices=TERM_CHOICES, validators=[DataRequired()])
    academic_year = StringField("Academic year", validators=[DataRequired(), Length(max=20)], render_kw={"placeholder": "2026"})
    cat_score = DecimalField("CAT score", validators=[DataRequired(), NumberRange(min=0, max=40)], places=2)
    exam_score = DecimalField("Exam score", validators=[DataRequired(), NumberRange(min=0, max=60)], places=2)
    submit = SubmitField("Save result")


class ActivityForm(FlaskForm):
    student_id = SelectField("Student", coerce=int, choices=[], validators=[DataRequired()])
    activity_name = StringField("Activity name", validators=[DataRequired(), Length(max=120)])
    activity_type = SelectField("Activity type", choices=ACTIVITY_TYPES, validators=[DataRequired()])
    participation_level = SelectField("Participation", choices=PARTICIPATION_LEVELS, validators=[DataRequired()])
    progress_percent = IntegerField("Progress %", validators=[DataRequired(), NumberRange(min=0, max=100)])
    progress_note = TextAreaField("Progress note", validators=[Optional(), Length(max=500)])
    submit = SubmitField("Add activity")


class AchievementForm(FlaskForm):
    student_id = SelectField("Student", coerce=int, choices=[], validators=[DataRequired()])
    title = StringField("Achievement title", validators=[DataRequired(), Length(max=120)])
    category = StringField("Category", validators=[DataRequired(), Length(max=40)])
    achievement_date = DateField("Date", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired(), Length(max=500)])
    submit = SubmitField("Add achievement")


class FeeStructureForm(FlaskForm):
    student_id = SelectField("Student", coerce=int, choices=[], validators=[DataRequired()])
    term = SelectField("Term", choices=TERM_CHOICES, validators=[DataRequired()])
    academic_year = StringField("Academic year", validators=[DataRequired(), Length(max=20)])
    total_amount = DecimalField("Total fees", validators=[DataRequired(), NumberRange(min=0)], places=2)
    due_date = DateField("Due date", validators=[DataRequired()])
    submit = SubmitField("Save fee structure")


class PaymentForm(FlaskForm):
    student_id = SelectField("Student", coerce=int, choices=[], validators=[DataRequired()])
    fee_structure_id = SelectField("Fee record", coerce=int, choices=[], validators=[DataRequired()])
    amount_paid = DecimalField("Amount paid", validators=[DataRequired(), NumberRange(min=0)], places=2)
    payment_date = DateField("Payment date", validators=[DataRequired()])
    reference = StringField("Receipt/reference", validators=[DataRequired(), Length(max=80)])
    submit = SubmitField("Record payment")


class MessageForm(FlaskForm):
    receiver_id = SelectField("Send to", coerce=int, choices=[], validators=[DataRequired()])
    student_id = SelectField("Student", coerce=int, choices=[], validators=[Optional()])
    category = SelectField("Category", choices=MESSAGE_CATEGORIES, validators=[DataRequired()])
    subject = StringField("Subject", validators=[DataRequired(), Length(max=120)])
    body = TextAreaField("Message", validators=[DataRequired(), Length(min=10, max=1000)])
    submit = SubmitField("Send update")


class HealthRecordForm(FlaskForm):
    student_id = SelectField("Student", coerce=int, choices=[], validators=[DataRequired()])
    term = SelectField("Term", choices=TERM_CHOICES, validators=[DataRequired()])
    academic_year = StringField("Academic year", validators=[DataRequired(), Length(max=20)])
    treatment = StringField("Treatment / vaccination", validators=[DataRequired(), Length(max=200)])
    notes = TextAreaField("Notes", validators=[Optional(), Length(max=1000)])
    submit = SubmitField("Save health status")


class ParentCommentForm(FlaskForm):
    student_id = SelectField("Student", coerce=int, choices=[], validators=[Optional()])
    category = SelectField("Category", choices=COMMENT_CATEGORIES, validators=[DataRequired()])
    comment = TextAreaField("Comment", validators=[DataRequired(), Length(min=8, max=1000)])
    submit = SubmitField("Post comment")


class AdmissionForm(FlaskForm):
    first_name = StringField("First name", validators=[DataRequired(), Length(max=80)])
    last_name = StringField("Last name", validators=[DataRequired(), Length(max=80)])
    admission_number = StringField("Admission number", validators=[DataRequired(), Length(max=30)])
    class_name = SelectField("Class", choices=CLASS_CHOICES, validators=[DataRequired()])
    stream = SelectField("Stream", choices=STREAM_CHOICES, validators=[DataRequired()])
    profile_photo = StringField("Profile photo URL", validators=[Optional(), Length(max=255)])
    parent_id = SelectField("Parent account", coerce=int, choices=[], validators=[Optional()])
    submit = SubmitField("Admit student")


class FinanceReportForm(FlaskForm):
    term = SelectField("Term", choices=TERM_CHOICES, validators=[DataRequired()])
    academic_year = StringField("Academic year", validators=[DataRequired(), Length(max=20)])
    title = StringField("Report title", validators=[DataRequired(), Length(max=120)])
    amount_collected = DecimalField("Amount collected", validators=[DataRequired(), NumberRange(min=0)], places=2)
    expected_amount = DecimalField("Expected amount", validators=[DataRequired(), NumberRange(min=0)], places=2)
    report_body = TextAreaField("Finance summary", validators=[DataRequired(), Length(min=10, max=3000)])
    submit = SubmitField("Send report to principal")
