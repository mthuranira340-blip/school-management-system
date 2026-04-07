from flask import Flask
from flask import render_template

from config import Config
from .extensions import csrf, db, login_manager
from .services import ensure_schema_updates, get_current_wallpaper, seed_demo_data, get_school_name


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    from .routes.auth import auth_bp
    from .routes.main import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    @app.context_processor
    def inject_school_meta():
        return {
            "school_name": get_school_name(),
            "current_wallpaper": get_current_wallpaper(),
        }

    @app.errorhandler(403)
    def forbidden(_error):
        return render_template("error.html", title="Access Denied", message="You do not have permission to perform that action."), 403

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("error.html", title="Page Not Found", message="The page you are looking for could not be found."), 404

    with app.app_context():
        db.create_all()
        ensure_schema_updates()
        if app.config.get("SEED_DEMO_DATA"):
            seed_demo_data()

    return app
