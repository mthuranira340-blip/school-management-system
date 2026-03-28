CREATE DATABASE IF NOT EXISTS high_school_management;
USE high_school_management;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    school_email VARCHAR(120) NOT NULL UNIQUE,
    phone_number VARCHAR(30) NULL,
    gender VARCHAR(20) NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'teacher', 'parent', 'finance') NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(80) NOT NULL,
    last_name VARCHAR(80) NOT NULL,
    admission_number VARCHAR(30) NOT NULL UNIQUE,
    portal_student_id VARCHAR(40) NOT NULL UNIQUE,
    class_name VARCHAR(40) NOT NULL,
    stream VARCHAR(40) NOT NULL,
    profile_photo VARCHAR(255) NULL,
    school_email VARCHAR(120) NOT NULL UNIQUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS parent_student_links (
    id INT AUTO_INCREMENT PRIMARY KEY,
    parent_id INT NOT NULL,
    student_id INT NOT NULL,
    CONSTRAINT fk_parent_link_user FOREIGN KEY (parent_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_parent_link_student FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS subjects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(80) NOT NULL,
    code VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    subject_id INT NOT NULL,
    term VARCHAR(30) NOT NULL,
    academic_year VARCHAR(20) NOT NULL,
    cat_score DECIMAL(5,2) NOT NULL DEFAULT 0,
    exam_score DECIMAL(5,2) NOT NULL DEFAULT 0,
    created_by_id INT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_result_student FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    CONSTRAINT fk_result_subject FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    CONSTRAINT fk_result_user FOREIGN KEY (created_by_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS fee_structures (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    term VARCHAR(30) NOT NULL,
    academic_year VARCHAR(20) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL DEFAULT 0,
    due_date DATE NOT NULL,
    CONSTRAINT fk_fee_student FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS fee_payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    fee_structure_id INT NOT NULL,
    amount_paid DECIMAL(10,2) NOT NULL,
    payment_date DATE NOT NULL,
    reference VARCHAR(80) NOT NULL,
    recorded_by VARCHAR(80) NOT NULL,
    CONSTRAINT fk_payment_student FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    CONSTRAINT fk_payment_fee FOREIGN KEY (fee_structure_id) REFERENCES fee_structures(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS activities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    activity_name VARCHAR(120) NOT NULL,
    activity_type VARCHAR(40) NOT NULL,
    participation_level VARCHAR(40) NOT NULL,
    progress_note TEXT NULL,
    progress_percent INT NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_activity_student FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS achievements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    title VARCHAR(120) NOT NULL,
    category VARCHAR(40) NOT NULL,
    description TEXT NOT NULL,
    achievement_date DATE NOT NULL,
    CONSTRAINT fk_achievement_student FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id INT NOT NULL,
    receiver_id INT NOT NULL,
    student_id INT NULL,
    category VARCHAR(40) NOT NULL,
    subject VARCHAR(120) NOT NULL,
    body TEXT NOT NULL,
    sent_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_message_sender FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_message_receiver FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_message_student FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS health_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    term VARCHAR(30) NOT NULL,
    academic_year VARCHAR(20) NOT NULL,
    treatment VARCHAR(200) NOT NULL,
    notes TEXT NULL,
    recorded_by_id INT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_health_student FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    CONSTRAINT fk_health_user FOREIGN KEY (recorded_by_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS parent_comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    parent_id INT NOT NULL,
    student_id INT NULL,
    category VARCHAR(40) NOT NULL,
    comment TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    admin_response TEXT NULL,
    CONSTRAINT fk_comment_parent FOREIGN KEY (parent_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_comment_student FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS finance_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    submitted_by_id INT NOT NULL,
    term VARCHAR(30) NOT NULL,
    academic_year VARCHAR(20) NOT NULL,
    title VARCHAR(120) NOT NULL,
    amount_collected DECIMAL(12,2) NOT NULL DEFAULT 0,
    expected_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    report_body TEXT NOT NULL,
    submitted_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    reviewed_by_admin_id INT NULL,
    reviewed_at DATETIME NULL,
    teacher_shared BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_report_finance FOREIGN KEY (submitted_by_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_report_admin FOREIGN KEY (reviewed_by_admin_id) REFERENCES users(id) ON DELETE SET NULL
);
