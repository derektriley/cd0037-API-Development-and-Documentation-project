import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random

from models import db, setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @DONE: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    cors = CORS(app, resources={r"/*": {"origins": "*"}})
    """
    @DONE: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
        return response
    """
    @DONE:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories', methods=["GET"])
    @cross_origin()
    def get_all_available_categories():
        cats = Category.query.all()
        data = {}
        data['categories'] = {}
        for c in cats:
            categories = data['categories']
            categories[c.id] = c.type
        return jsonify(data);

    """
    @DONE:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions', methods=["GET"])
    @cross_origin()
    def get_questions():
        # Implement pagination
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * 10
        end = start + 10

        questions = Question.query.order_by(Question.id).all()
        totalQuestions = len(questions)
        formattedQuestions = [question.format() for question in questions[start:end]]
        cats = Category.query.all()
        data = {}
        data['questions'] = formattedQuestions
        data['totalQuestions'] = totalQuestions
        data['categories'] = {}
        for c in cats:
            categories = data['categories']
            categories[c.id] = c.type
        data['currentCategory'] = 'History'
        return jsonify(data)

    """
    @DONE:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=["DELETE"])
    def delete_question(question_id):
        question = Question.query.get(question_id)
        try:
            question.delete()
        except:
            db.session.rollback()
            return jsonify({
                'success': False}), 404
        finally:
            db.session.close()

        return jsonify({
            'success': True,
            'question_id': question_id})

    """
    @DONE:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=["POST"])
    @cross_origin()
    def post_question():
        json = request.get_json()

        searchTerm = json.get('searchTerm', None)
        if searchTerm:
            questions = (Question.query
                                .filter(Question.question.ilike(f'%{searchTerm}%'))
                                .all())
            formattedQuestions = [question.format() for question in questions]

            return jsonify({
                'questions': formattedQuestions,
                'totalQuestions': len(questions),
                'currentCategory': 'Entertainment'
            })
        # We are inserting a new question
        newQuestion = Question(json.get('question', None),
                               json.get('answer', None),
                               json.get('category', None),
                               json.get('difficulty', None))

        try:
            newQuestion.insert()
        except:
            db.session.rollback()
            return jsonify({
                'success': True
                }), 500
        finally:
            db.session.close()

        return jsonify({
            'success': True
        })

    """
    @DONE Above:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    """
    @DONE:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions', methods=["GET"])
    @cross_origin()
    def get_questions_by_category(category_id):
        questions = (Question.query
                                .filter(Question.category == category_id)
                                .all())
        formattedQuestions = [question.format() for question in questions]

        return jsonify({
            'questions': formattedQuestions,
            'totalQuestions': len(questions),
            'currentCategory': 'History'
        })


    """
    @DONE:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=["POST"])
    def play_quiz():
        json = request.get_json()
        givenCategory = json.get("quiz_category", None)
        previousQuestions = json.get("previous_questions", [])
        if givenCategory != 0:
            questions = (Question.query
                                .filter(Question.category == givenCategory)
                                .filter(Question.id not in previousQuestions)
                                .all())
        else:
            questions = (Question.query
                                .filter(Question.id not in previousQuestions)
                                .all())
        randomQuestion = random.choice(questions)

        return jsonify({
            "question": randomQuestion.format()
        })

    """
    @DONE:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable Entity"
        }), 422

    @app.errorhandler(500)
    def unprocessable_entity(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Server encountered an error"
        }), 500

    return app

