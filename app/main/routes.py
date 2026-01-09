from flask import Blueprint, render_template, request, jsonify
from app.models import QuizAttempt, Category
from flask import session
from app import db
from sqlalchemy import and_
import uuid

main_bp = Blueprint("main", __name__)

def get_user_id_from_header():
    """
    Get user_id from X-User-Id header (set by Gateway after JWT validation).
    This is the ONLY source of user identity - no Flask-Login, no current_user.
    
    Returns:
        int: user_id if authenticated, None if guest
    """
    # Check both cases (some proxies may lowercase headers)
    user_id_header = request.headers.get('X-User-Id') or request.headers.get('x-user-id')
    
    if user_id_header and user_id_header.strip():
        try:
            return int(user_id_header.strip())
        except (ValueError, TypeError):
            return None
    return None

def get_or_create_session_id():
    """
    Get or create a unique session ID for anonymous users.
    CRITICAL: Only call this for GUEST users. Logged-in users should NOT have session_id.
    """
    if 'anonymous_session_id' not in session:
        session['anonymous_session_id'] = str(uuid.uuid4())
        session.permanent = False
    return session.get('anonymous_session_id')

def clear_guest_session():
    """
    Clear guest session ID. Call this when user logs in to prevent guest identity persistence.
    """
    if 'anonymous_session_id' in session:
        session.pop('anonymous_session_id')
        session.modified = True

@main_bp.route("/")
def home():
    session.pop("active_quiz", None)
    session.pop("current_question", None)
    session.pop("answers", None)
    session.pop("category", None)
    if session.get("active_quiz") and not session.get("question_ids"):
        session.pop("active_quiz", None)
    
    # Get user identity from X-User-Id header (ONLY source of identity)
    user_id = get_user_id_from_header()
    
    if user_id is None:
        # Guest user - ensure session_id exists
        get_or_create_session_id()
    else:
        # Logged-in user - clear any guest session_id to prevent identity mixing
        clear_guest_session()

    categories = Category.query.all()
    return render_template("home.html", categories=categories)

@main_bp.route("/history")
def history():
    """
    Display quiz history with strict result isolation:
    - Logged-in users: Only see their own results (user_id matches, user_id IS NOT NULL)
    - Guest users: Only see their own guest results (user_id IS NULL, session_id matches)
    
    Identity Source: X-User-Id header (set by Gateway after JWT validation)
    """
    user_id = get_user_id_from_header()
    session_id = session.get('anonymous_session_id')
    
    if user_id is not None:
        clear_guest_session()
        query = QuizAttempt.query.filter(
            and_(
                QuizAttempt.user_id.isnot(None),
                QuizAttempt.user_id == user_id
            )
        ).order_by(QuizAttempt.created_at.desc())
        quizzes = query.all()
    else:
        session_id = get_or_create_session_id()
        query = QuizAttempt.query.filter(
            and_(
                QuizAttempt.user_id.is_(None),
                QuizAttempt.session_id == session_id
            )
        ).order_by(QuizAttempt.created_at.desc())
        quizzes = query.all()
    
    return render_template("history.html", history=quizzes)

@main_bp.route("/clear-session", methods=["POST"])
def clear_session():
    """
    Clear Flask session - used when user logs out to reset anonymous session.
    CRITICAL: This only clears the Flask session, NOT database records.
    Quiz results are NEVER deleted - they persist forever.
    """
    session.clear()
    return '', 204  # No content


@main_bp.route("/migrate-guest-results", methods=["POST"])
def migrate_guest_results():
    """
    Migrate guest quiz results to user_id when user logs in.
    This ensures guest results created before login are associated with the user account.
    
    Identity Source: X-User-Id header (set by Gateway after JWT validation)
    
    Expected headers:
    - X-User-Id: The user ID to migrate results to
    
    Expected body (JSON):
    - session_id: The guest session ID to migrate from (optional, uses current session if not provided)
    
    Returns:
    - Number of results migrated
    """
    # Get user identity from X-User-Id header (ONLY source of identity)
    user_id = get_user_id_from_header()
    
    if user_id is None:
        return jsonify({'error': 'X-User-Id header is required and must be valid'}), 400
    
    # Get session_id from request body or current session
    data = request.get_json() or {}
    session_id = data.get('session_id') or session.get('anonymous_session_id')
    
    if not session_id:
        # No guest session to migrate
        return jsonify({
            'migrated': 0,
            'message': 'No guest session found to migrate'
        }), 200
    
    guest_quizzes = QuizAttempt.query.filter(
        and_(
            QuizAttempt.user_id.is_(None),
            QuizAttempt.session_id == session_id
        )
    ).all()
    
    migrated_count = 0
    for quiz in guest_quizzes:
        quiz.user_id = user_id
        quiz.session_id = None
        migrated_count += 1
    
    if migrated_count > 0:
        db.session.commit()
    
    clear_guest_session()
    
    return jsonify({
        'migrated': migrated_count,
        'user_id': user_id,
        'message': f'Migrated {migrated_count} guest quiz results to user account'
    }), 200
