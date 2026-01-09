from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.secret_key = "dev-secret-key"
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_TYPE'] = 'filesystem'

    # Ensure instance directory exists
    instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'instance')
    os.makedirs(instance_path, exist_ok=True)
    
    # Use absolute path for database
    db_path = os.path.join(instance_path, 'quiz.db')
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from app.main.routes import main_bp
    from app.quiz.routes import quiz_bp
    from app.api.routes import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(quiz_bp, url_prefix="/quiz")
    app.register_blueprint(api_bp)

    with app.app_context():
        db.create_all()
        
    from datetime import timedelta
    app.jinja_env.globals.update(timedelta=timedelta)


    return app

