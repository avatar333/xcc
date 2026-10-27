import os
import secrets
from pathlib import Path

from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = "auth.login"

def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY="dev-change-me", SQLALCHEMY_DATABASE_URI="sqlite:///xcom.sqlite3", SQLALCHEMY_TRACK_MODIFICATIONS=False, UPLOAD_FOLDER=str(Path(app.instance_path) / "uploads"), MAX_CONTENT_LENGTH=8 * 1024 * 1024)
    if config: app.config.update(config)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    db.init_app(app); migrate.init_app(app, db); login_manager.init_app(app)
    app.config.setdefault("SESSION_COOKIE_HTTPONLY", True); app.config.setdefault("SESSION_COOKIE_SAMESITE", "Lax")
    @app.context_processor
    def security_context():
        from flask import session
        session.setdefault("csrf_token", secrets.token_urlsafe(32))
        return {"csrf_token_value": session["csrf_token"]}
    @app.before_request
    def validate_csrf():
        from flask import request, session
        if request.method == "POST" and not app.config.get("TESTING") and request.form.get("csrf_token") != session.get("csrf_token"):
            from flask import abort
            abort(400, description="CSRF validation failed")
    from app import models  # noqa: F401
    from app.commands import register_commands
    register_commands(app)
    from app.routes import (
        auth,
        avenger,
        catalogue,
        equipment,
        main,
        playthroughs,
        research,
        soldiers,
    )
    app.register_blueprint(auth.bp); app.register_blueprint(main.bp); app.register_blueprint(playthroughs.bp); app.register_blueprint(catalogue.bp); app.register_blueprint(avenger.bp); app.register_blueprint(soldiers.bp); app.register_blueprint(equipment.bp); app.register_blueprint(research.bp)
    with app.app_context():
        if not os.environ.get("XCOM_SKIP_SCHEMA_CREATE"):
            db.create_all()
            from app.services.seed import seed_admin, seed_builtin_packs
            seed_builtin_packs(); seed_admin()
    return app
