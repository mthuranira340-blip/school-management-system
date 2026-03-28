import os


def resolve_database_url():
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        return database_url

    mysql_user = os.environ.get("MYSQL_USER")
    mysql_password = os.environ.get("MYSQL_PASSWORD")
    mysql_host = os.environ.get("MYSQL_HOST", "localhost")
    mysql_port = os.environ.get("MYSQL_PORT", "3306")
    mysql_db = os.environ.get("MYSQL_DB", "high_school_management")

    if mysql_user and mysql_password:
        return f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_db}"

    # SQLite fallback keeps the demo runnable when MySQL is not configured locally.
    return "sqlite:///high_school_management_demo.db"


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    SQLALCHEMY_DATABASE_URI = resolve_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LOW_GRADE_THRESHOLD = os.environ.get("LOW_GRADE_THRESHOLD", "C")
    PREFERRED_URL_SCHEME = "https"
    SESSION_COOKIE_SECURE = os.environ.get("FLASK_ENV") == "production"
    REMEMBER_COOKIE_SECURE = os.environ.get("FLASK_ENV") == "production"
