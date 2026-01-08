from flask import Blueprint, render_template, request
from app.models import QuizAttempt, Category
from flask import session

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def home():
    session.pop("active_quiz", None)
    session.pop("current_question", None)
    session.pop("answers", None)
    session.pop("category", None)
    if session.get("active_quiz") and not session.get("question_ids"):
        session.pop("active_quiz", None)

    categories = Category.query.all()
    return render_template("home.html", categories=categories)

@main_bp.route("/history")
def history():
    # Get user_id from header set by Gateway (if JWT was validated)
    user_id_header = request.headers.get('X-User-Id')
    
    if user_id_header and user_id_header.strip():  # Check if not empty or whitespace
        try:
            # User is logged in - show only this user's attempts
            user_id = int(user_id_header)
            quizzes = QuizAttempt.query.filter_by(user_id=user_id).order_by(
                QuizAttempt.created_at.desc()
            ).all()
        except (ValueError, TypeError):
            # Invalid user_id, treat as anonymous
            quizzes = QuizAttempt.query.filter_by(user_id=None).order_by(
                QuizAttempt.created_at.desc()
            ).all()
    else:
        # User is not logged in - show only anonymous attempts (guest results)
        quizzes = QuizAttempt.query.filter_by(user_id=None).order_by(
            QuizAttempt.created_at.desc()
        ).all()

    return render_template("history.html", history=quizzes)
