from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.secret_key = "dev-secret-key"

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///quiz.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from app.main.routes import main_bp
    from app.quiz.routes import quiz_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(quiz_bp, url_prefix="/quiz")

    with app.app_context():
        db.create_all()
        
    from datetime import timedelta
    app.jinja_env.globals.update(timedelta=timedelta)


    return app

