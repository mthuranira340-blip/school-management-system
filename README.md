# High School Management System

A full-stack Flask school management system for administrators, teachers, parents, and finance staff. It includes role-based authentication, student profiles, results analytics, fee management, co-curricular tracking, health tracking, parent feedback, admissions, messaging, finance reporting, and PDF report card export.

## Stack

- Frontend: HTML, CSS, JavaScript, Chart.js, Bootstrap
- Backend: Python, Flask, Flask-Login, Flask-SQLAlchemy
- Database: MySQL via `PyMySQL`
- Demo fallback: SQLite when MySQL environment variables are not set

## Core Features

- Secure login with `admin`, `teacher`, `parent`, and `finance` roles
- Parent-to-student linking
- Parent quick portal access using student name and auto-generated student portal ID
- Student profile pages with admission details, class, stream, photo, school email, achievements, activities, health status, and results
- Student view includes linked parent contact details such as phone number, gender, and email
- Teacher/admin academic tools for subjects, CAT scores, exam scores, automatic totals, averages, grades, GPA, and low-grade alerts
- Fees setup, payment recording, balance tracking, and payment history
- Parent dashboard with student performance, fee summary, activities, achievements, health status, and notifications
- Health status records so parents can see what their child has been treated against within the term
- Parent comment section for performance review and school development ideas
- Separate admissions page for new student enrollment
- Finance reporting workflow where finance submits reports to the principal and the principal shares them with teachers
- School messaging for announcements, weekend travel notices, fee updates, and co-curricular updates
- PDF report card export
- Student search and filter
- Sample data for testing

## Demo Accounts

- Admin: `admin@demo.local` / `admin123`
- Teacher: `teacher@demo.local` / `teacher123`
- Parent: `parent@demo.local` / `parent123`
- Finance: `finance@demo.local` / `finance123`
- Parent quick access demo: student name `Amina Kamau` with portal ID `STU-ADM001`

## Project Structure

```text
app/
  routes/
    auth.py
    main.py
  static/
    css/style.css
    js/app.js
  templates/
    base.html
    login.html
    register.html
    dashboard.html
    admissions.html
    students.html
    academics.html
    health.html
    comments.html
    finance.html
    fees.html
    messages.html
    student_profile.html
  __init__.py
  extensions.py
  forms.py
  models.py
  services.py
config.py
run.py
schema.sql
requirements.txt
```

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set environment variables for MySQL if you want to use MySQL:

```bash
set MYSQL_USER=root
set MYSQL_PASSWORD=your_password
set MYSQL_HOST=localhost
set MYSQL_PORT=3306
set MYSQL_DB=high_school_management
set SECRET_KEY=change-me
```

4. Create the MySQL schema:

```bash
mysql -u root -p < schema.sql
```

5. Run the app:

```bash
python run.py
```

If the system Python launcher is unavailable on your machine, this project also supports the local portable runtime created during repair:

```bash
.\.python312\python.exe run.py
```

6. Open `http://127.0.0.1:5000`.

## Notes

- If MySQL is not configured, the app automatically runs with a local SQLite demo database.
- The app no longer seeds demo users by default. Run `python scripts/reset_accounts.py` to drop and recreate the schema, then register whatever accounts you need yourself.
- If you still see schema errors after updating the code, rerun the reset script so the new `wallpaper` column is created.
- Set `SEED_DEMO_DATA=true` before starting the app if you ever want the demo accounts automatically seeded again.
- School emails are auto-generated in the format `identifier@greenfieldhigh.edu`.
- The `.python312` folder can act as a self-contained local Python environment when the global Python installation is broken or missing.

## Database Tables

- `users`
- `students`
- `parent_student_links`
- `subjects`
- `results`
- `fee_structures`
- `fee_payments`
- `activities`
- `achievements`
- `messages`
- `health_records`
- `parent_comments`
- `finance_reports`
