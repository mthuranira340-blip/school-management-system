from pathlib import Path

OUTPUT_FILE = "School_Management_System_Documentation.rtf"


def build_document():
    content = r'''{\rtf1\ansi\deff0
{\fonttbl{\f0 Arial;}{\f1 Courier New;}}
\fs24
\b High School Management System Documentation\b0\par
\par
\b 1. Introduction\b0\par
The High School Management System is a full-stack web application built to support school administration, academic tracking, parent engagement, student admissions, finance reporting, health updates, and transfer clearance workflows. The system is designed for four user roles: Admin, Teacher, Parent, and Finance.\par
\par
\b 2. Technology Stack\b0\par
Frontend: HTML, CSS, JavaScript, Bootstrap, Chart.js\par
Backend: Python, Flask, Flask-Login, Flask-SQLAlchemy\par
Database: MySQL using PyMySQL\par
Fallback database: SQLite for demo and local testing\par
\par
\b 3. User Roles\b0\par
Admin:\par
- Manages the whole system\par
- Changes the school name from settings\par
- Reviews transfer clearance letters\par
- Applies the digital stamp and approves transfers\par
- Reviews finance reports before sharing them with teachers\par
\par
Teacher:\par
- Adds and manages students\par
- Assigns subjects being undertaken by each student\par
- Records CAT and exam results\par
- Adds co-curricular activities and achievements\par
- Records health status updates\par
- Starts student transfer requests\par
\par
Parent:\par
- Views linked student performance, fees, activities, achievements, and health records\par
- Reads messages and notifications\par
- Posts comments on performance and school development\par
- Can use the student name and portal ID for quick access to the parent portal\par
\par
Finance:\par
- Prepares and submits finance reports to the principal\par
- Tracks fee collection summaries\par
\par
\b 4. Main Features\b0\par
\b 4.1 Authentication and Access Control\b0\par
- Secure sign-in for Admin, Teacher, Parent, and Finance users\par
- Parent accounts are linked to a specific student\par
- Parent quick portal access uses the student full name and portal ID\par
\par
\b 4.2 School Identity Settings\b0\par
- The Admin can change the school name from the Settings page\par
- The chosen school name appears in the sidebar, page title, and generated transfer letters\par
- Generated school emails use the current school identity for new records\par
\par
\b 4.3 Student Management\b0\par
- Add student records with full name, admission number, class, stream, photo, and linked parent\par
- Automatic generation of student portal ID\par
- Automatic generation of school email\par
- Search and filter students\par
- Selected student remains constant across pages until changed by the teacher or parent\par
\par
\b 4.4 Academic Tracker\b0\par
The Academic Tracker is separated from the general school management tools so academic work is easier to focus on.\par
- Add subjects\par
- Assign subjects to students\par
- Record CAT and exam scores\par
- Auto-calculate total marks, average score, grade, and GPA\par
- Track recent results\par
- Track co-curricular activities and achievements\par
- Display charts for trends and subject performance\par
\par
\b 4.5 Health Tracking\b0\par
- Teachers and administrators can record health treatments by term\par
- Parents can see what their child has been treated against during the term\par
\par
\b 4.6 Fees Management\b0\par
- Set fee structures\par
- Record fee payments\par
- Display total, paid amount, balance, and payment history\par
- Show fee status as Paid, Pending, or Overdue\par
\par
\b 4.7 Parent Feedback and Comments\b0\par
- Parents can post comments about student performance\par
- Parents can also give ideas or feedback on school development\par
- Teachers and administrators can review the submitted comments\par
\par
\b 4.8 Messaging and Notifications\b0\par
- Internal message panel for announcements and notices\par
- Supports weekend travel notices, co-curricular updates, academic notices, and fee updates\par
- Admin receives notifications for transfer clearance approval\par
- Teachers receive notifications when a transfer is approved\par
\par
\b 4.9 Admissions\b0\par
- Dedicated admissions page for enrolling new students\par
- Parent can be linked during the admission process\par
\par
\b 4.10 Finance Workflow\b0\par
- Finance submits reports to the principal\par
- Admin reviews and shares reports with teachers\par
- Teachers only see reports approved and shared by the principal\par
\par
\b 4.11 Transfer Clearance Workflow\b0\par
- Teacher initiates a student transfer request\par
- The system auto-generates a clearance letter covering the Principal's Office, Class Teacher, Finance Office, Health Office, Academics Office, and Co-curricular Office\par
- Only the Admin can open and review the clearance letter\par
- The Admin approves the request and applies a digital stamp\par
- After approval, the student is archived from active lists instead of being hard-deleted, so the history remains safe\par
\par
\b 5. Project Structure\b0\par
\f1
app/\par
  routes/\par
    auth.py\par
    main.py\par
  static/\par
    css/style.css\par
    js/app.js\par
  templates/\par
    base.html\par
    login.html\par
    register.html\par
    dashboard.html\par
    admissions.html\par
    students.html\par
    academics.html\par
    health.html\par
    comments.html\par
    finance.html\par
    fees.html\par
    messages.html\par
    transfers.html\par
    settings.html\par
    student_profile.html\par
  __init__.py\par
  extensions.py\par
  forms.py\par
  models.py\par
  services.py\par
config.py\par
run.py\par
schema.sql\par
requirements.txt\par
\f0
\par
\b 6. Database Tables\b0\par
- users\par
- site_settings\par
- students\par
- parent_student_links\par
- subjects\par
- student_subjects\par
- results\par
- fee_structures\par
- fee_payments\par
- activities\par
- achievements\par
- messages\par
- health_records\par
- parent_comments\par
- finance_reports\par
- transfer_clearances\par
\par
\b 7. Setup Instructions\b0\par
1. Open PowerShell in the project folder.\par
2. Install dependencies with pip install -r requirements.txt.\par
3. Run the app with python run.py.\par
4. Open http://127.0.0.1:5000 in the browser.\par
\par
\b 8. Demo Accounts\b0\par
Admin: admin@demo.local / admin123\par
Teacher: teacher@demo.local / teacher123\par
Parent: parent@demo.local / parent123\par
Finance: finance@demo.local / finance123\par
\par
\b 9. Conclusion\b0\par
This system combines school administration, academics, parent communication, finance visibility, health tracking, and transfer governance in one responsive platform.\par
}'''
    Path(OUTPUT_FILE).write_text(content, encoding="utf-8")
    print(f"Documentation generated: {OUTPUT_FILE}")


if __name__ == "__main__":
    build_document()
