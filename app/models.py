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
