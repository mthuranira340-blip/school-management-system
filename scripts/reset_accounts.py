from app import create_app
from app.extensions import db


def reset_accounts():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("Database reset complete. Run the app and register new accounts.")


if __name__ == "__main__":
    reset_accounts()
