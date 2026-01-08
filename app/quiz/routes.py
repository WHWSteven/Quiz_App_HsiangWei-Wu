from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from datetime import datetime
from app import db
from app.models import QuizAttempt, QuizAnswer, Category, Choice
import random
from app.models import Question
from sqlalchemy.sql import func


quiz_bp=Blueprint('quiz',__name__)
@quiz_bp.route("/start", methods=["POST"])
def start_quiz():
    #  Enforce single active quiz by resetting any previous one
    session.pop("question_ids", None)
    session.pop("answers", None)
    session.pop("category_id", None)

    category_id = request.form.get("category_id")
    if not category_id:
        flash("Please select a category.")
        return redirect(url_for("main.home"))

    category = Category.query.get(int(category_id))
    if not category:
        flash("Invalid category.")
        return redirect(url_for("main.home"))

    session["category_id"] = category.id

    questions = (
        Question.query
        .filter_by(category_id=category.id)
        .order_by(func.random())
        .limit(5)
        .all()
    )

    if len(questions) < 5:
        flash("Not enough questions in this category.")
        return redirect(url_for("main.home"))

    session["question_ids"] = [q.id for q in questions]
    session["answers"] = {}

    return redirect(url_for("quiz.question", index=1))



@quiz_bp.route("/question/<int:index>", methods=["GET", "POST"])
def question(index):
    # print("SESSION AFTER POST:", session.get("answers"))
    question_ids = session.get("question_ids")
    if not question_ids:
        flash("No active quiz.")
        return redirect(url_for("main.home"))

    total = len(question_ids)
    if index < 1 or index > total:
        flash("Invalid question.")
        return redirect(url_for("main.home"))

    question_id = question_ids[index - 1]
    question = Question.query.get(question_id)

    
    choice_order_key = f"choice_order_{question_id}"

    if choice_order_key not in session:
        choices = list(question.choices)
        random.shuffle(choices)
        session[choice_order_key] = [c.id for c in choices]
        session.modified = True
    else:
        choices = (
            Choice.query
            .filter(Choice.id.in_(session[choice_order_key]))
            .all()
        )
        # preserve order
        choices.sort(key=lambda c: session[choice_order_key].index(c.id))


    if request.method == "POST":
        answer = request.form.get(f"answer_{question_id}")
        if not answer:
            flash("Please select an answer.")
            return redirect(url_for("quiz.question", index=index))

        #  store choice_id as INT
        session["answers"][str(question_id)] = int(answer)
        session.modified = True

        if index < total:
            return redirect(url_for("quiz.question", index=index + 1))
        else:
            return redirect(url_for("quiz.submit"))
        
    print("SESSION CONTENT:", dict(session))
    print("ANSWERS:", session.get("answers"))
    print("CURRENT QUESTION ID:", question_id)
    print("----------")
    print("EXPECTING ANSWER FOR:", question_id)
    print("FOUND:", session["answers"].get(str(question_id)))


    return render_template(
        "quiz_question.html",
        question=question,
        choices=choices,
        index=index,
        total=total
    )


def letter_to_index(letter: str) -> int:
    return ord(letter.upper()) - ord("A")

@quiz_bp.route("/submit", methods=["POST"])
def submit():
    answers = session.get("answers", {})
    question_ids = session.get("question_ids", [])
    total = len(question_ids)

    # SAVE LAST QUESTION ANSWER FIRST (THIS FIXES THE BUG)
    last_qid = question_ids[-1] if question_ids else None
    last_answer = request.form.get(f"answer_{last_qid}")

    if last_qid and last_answer:
        answers[str(last_qid)] = int(last_answer)
        session["answers"] = answers
        session.modified = True


    # NOW validation works
    if len(answers) < total:
        flash("Please answer all questions before submitting.")
        return redirect(url_for("quiz.question", index=total))

    # Get user_id from header set by Gateway (if JWT was validated)
    user_id_header = request.headers.get('X-User-Id')
    if user_id_header and user_id_header.strip():
        try:
            user_id = int(user_id_header)
        except (ValueError, TypeError):
            user_id = None  # Invalid user_id, treat as anonymous
    else:
        user_id = None  # No user_id header, anonymous attempt
    
    quiz = QuizAttempt(
        category_id=session["category_id"],
        user_id=user_id,
        score=0,
        total=total
    )
    db.session.add(quiz)
    db.session.commit()

    score = 0

    for q_id in question_ids:
        selected_choice_id = answers.get(str(q_id))
        question = Question.query.get(q_id)

        if not selected_choice_id or not question:
            continue

        selected_choice = Choice.query.get(selected_choice_id)

        ordered_choices = (
            Choice.query
            .filter_by(question_id=q_id)
            .order_by(Choice.id)
            .all()
        )

        correct_index = letter_to_index(question.correct_choice)
        correct_text = (
            ordered_choices[correct_index].text
            if 0 <= correct_index < len(ordered_choices)
            else None
        )

        selected_text = selected_choice.text if selected_choice else None

        if selected_text and selected_text == correct_text:
            score += 1

        db.session.add(
            QuizAnswer(
                quiz_attempt_id=quiz.id,
                question_id=q_id,
                selected_choice=selected_text
            )
        )

    quiz.score = score
    db.session.commit()

   # clear quiz state
    for key in list(session.keys()):
        if key.startswith("choice_order_"):
            session.pop(key)

    session.pop("category_id", None)
    session.pop("question_ids", None)
    session.pop("answers", None)


    return redirect(url_for("quiz.detail", quiz_id=quiz.id))







@quiz_bp.route("/result")
def result():
    return render_template("quiz_result.html")
def letter_to_index(letter: str) -> int:
    return ord(letter.upper()) - ord("A")

@quiz_bp.route("/detail/<int:quiz_id>")
def detail(quiz_id):
    quiz = QuizAttempt.query.get(quiz_id)
    if not quiz:
        flash("Quiz not found.")
        return redirect(url_for("main.history"))
    
    # If user is authenticated, ensure they can only see their own quizzes
    # If user is anonymous, they can only see anonymous quizzes
    user_id_header = request.headers.get('X-User-Id')
    
    if user_id_header and user_id_header.strip():
        try:
            user_id = int(user_id_header)
            # Logged in user - can only see their own quizzes
            if quiz.user_id != user_id:
                flash("You don't have permission to view this quiz.")
                return redirect(url_for("main.history"))
        except (ValueError, TypeError):
            # Invalid user_id, treat as anonymous
            if quiz.user_id is not None:
                flash("You don't have permission to view this quiz.")
                return redirect(url_for("main.history"))
    else:
        # Anonymous user - can only see anonymous quizzes
        if quiz.user_id is not None:
            flash("You don't have permission to view this quiz.")
            return redirect(url_for("main.history"))

    rows = (
        db.session.query(QuizAnswer, Question)
        .join(Question, QuizAnswer.question_id == Question.id)
        .filter(QuizAnswer.quiz_attempt_id == quiz.id)
        .all()
    )

    results = []
    for ans, question in rows:
        choices = (
            Choice.query
            .filter_by(question_id=question.id)
            .order_by(Choice.id)
            .all()
        )

        correct_idx = letter_to_index(question.correct_choice)
        correct_text = choices[correct_idx].text if 0 <= correct_idx < len(choices) else "N/A"

        results.append({
            "question_text": question.text,
            "selected_text": ans.selected_choice,
            "correct_text": correct_text,
            "is_correct": ans.selected_choice == correct_text
        })

    return render_template("quiz_detail.html", quiz=quiz, results=results)



