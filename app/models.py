from datetime import datetime
from app import db

class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    questions = db.relationship("Question", backref="category")

class Question(db.Model):
    __tablename__ = "questions"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    correct_choice = db.Column(db.String(1), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))

    choices = db.relationship("Choice", backref="question")

class Choice(db.Model):
    __tablename__ = "choices"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"))


class QuizAttempt(db.Model):
    __tablename__ = "quiz_attempts"

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    user_id = db.Column(db.Integer, nullable=True)  # None for anonymous attempts
    session_id = db.Column(db.String(255), nullable=True, index=True)  # Flask session ID for anonymous users
    score = db.Column(db.Integer)
    total = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    category = db.relationship("Category")



class QuizAnswer(db.Model):
    __tablename__ = "quiz_answers"

    id = db.Column(db.Integer, primary_key=True)
    quiz_attempt_id = db.Column(db.Integer)
    question_id = db.Column(db.Integer)
    selected_choice = db.Column(db.String(1))


class UserProfile(db.Model):
    """
    User Profile model for Quiz Service.
    Stores user preferences and profile information in the Quiz Service.
    This is part of the Saga pattern where user registration creates
    both a user (User Service) and a profile (Quiz Service).
    """
    __tablename__ = "user_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique=True, nullable=False, index=True)
    notifications_enabled = db.Column(db.Boolean, default=True)
    default_category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    default_category = db.relationship("Category", foreign_keys=[default_category_id])

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'notifications_enabled': self.notifications_enabled,
            'default_category_id': self.default_category_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }