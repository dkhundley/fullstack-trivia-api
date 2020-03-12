import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

# HELPERS SETUP
# -----------------------------------------------------------------------------
# Setting up separate method to handle pagination


def paginate_questions(request, selection):
    # Getting page number from CLI argument
    page = request.args.get('page', 1, type=int)

    # Setting start / end points based on static QUESTIONS_PER_PAGE variable
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    # Applying pagination to incoming question set
    questions = [question.format() for question in selection]
    paginated_questions = questions[start:end]

    # Returning appropriately paginated questions
    return paginated_questions


# FULL FLASK APP SETUP
# -----------------------------------------------------------------------------
def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__)
    setup_db(app)

    # CORS / ACCESS SETUP
    # ---------------------------------------------------------------------------
    # Establishing CORS for our FLask app
    CORS(app)

    # Adding access control headers to incoming requests
    @app.after_request
    def add_access_control(response):
        # Adding proper authorization type
        response.headers.add(
            'Access-Control-Allow-Headers',
            'ContentType,Authorization, True')

        # Adding allowed methods (which is all of them)
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET,POST,PUT,DELETE,UPDATE,OPTIONS')

        # Returning adjusted response
        return response

    # 'GET' ENDPOINT SETUP
    # ---------------------------------------------------------------------------
    # Defining endpoint to handle GET requests for available categories
    @app.route('/categories', methods=['GET'])
    def get_categories():
        # Querying categories ordered by type using SQLAlchemy
        categories = Category.query.order_by(Category.type).all()

        # Handling 404 error issues if valid
        if len(categories) == 0:
            abort(404)

        # Returning proper response
        return jsonify({'success': True, 'categories': {
                       category.id: category.type for category in categories}})

    # Defining endpoint to handle GET requests for questions and correlated
    # categoiry
    @app.route('/questions', methods=['GET'])
    def get_questions():
        # Querying questions ordered by ID using SQLAlchemy
        questions = Question.query.order_by(Question.id).all()
        # Paginating questions with helper method
        paginated_questions = paginate_questions(request, questions)

        # Querying categories ored by type using SQLAlchemy
        categories = Category.query.order_by(Category.type).all()

        # Handling 404 error issues if valid
        if len(paginated_questions) == 0:
            abort(404)

        # Return valid information
        return jsonify({
            'success': True,
            'questions': paginated_questions,
            'total_questions': len(questions),
            'categories': {category.id: category.type for category in categories},
            'current_category': None
        })

    # Creating endpoint to return only questions of a specific category
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_category_questions(category_id):
        # Querying all questions based on the inputted category_id
        questions = Question.query.filter(
            Question.category == category_id).all()

        # Handling error scenarios
        if len(questions) == 0:
            abort(404)

        # Returning proper information if info is present
        return jsonify({
            'success': True,
            'questions': [question.format() for question in questions],
            'total_questions': len(questions),
            'current_category': category_id
        })

    # 'DELETE' ENDPOINT SETUP
    # ---------------------------------------------------------------------------
    # Defining endpoint for deleting a question based on question_id
    @app.route('/questions/<question_id>', methods=['DELETE'])
    def delete_question(question_id):
        # Setting up try block for execution of deletion
        try:
            # Quering the question with the question_id
            question = Question.query.get(question_id)

            # Deleting the question
            question.delete()

            # Returning success info
            return jsonify({
                'success': True,
                'deleted': question_id
            })
        # Handling error scenarios as 422 error
        except BaseException:
            abort(422)

    # 'POST' ENDPOINT SETUP
    # ---------------------------------------------------------------------------
    # Creating endpoint to add new questions in POST method
    @app.route('/questions', methods=['POST'])
    def create_question():
        # Getting body data from POST request
        body = request.get_json()

        # Pulling info from body into respective variables
        question = body.get('question')
        answer = body.get('answer')
        difficulty = body.get('difficulty')
        category = body.get('category')

        # Checking if body information is available
        if not (question and answer and difficulty and category):
            abort(422)

        # Creating try block to insert new question into database
        try:
            # Instantiating new question as Question object
            new_question = Question(question=question,
                                    answer=answer,
                                    difficulty=difficulty,
                                    category=category)

            # Inserting new question into database
            new_question.insert()

            # Returning success information
            return jsonify({
                'success': True,
                'created': new_question.id
            })
        # Handling error scenarios
        except BaseException:
            abort(422)

    # Creating endpoint for searching for a question based on a search term
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        # Getting body data from POST request
        body = request.get_json()

        # Pulling search term from body
        search_term = body.get('searchTerm')

        # Returning search results if search term present
        if search_term:
            search_results = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')).all()

            return jsonify({
                'success': True,
                'questions': [question.format() for question in search_results],
                'total_questions': len(search_results),
                'current_category': None
            })

        # Throwing error if invalid search term provided
        abort(404)

    # Creating endpoint to actually play a quiz
    @app.route('/quiz', methods=['POST'])
    def play_quiz():

        try:
            # Getting body data from POST request
            body = request.get_json()

            # Ensuring data is present from POST request
            if not ('quiz_category' in body and 'previous_questions' in body):
                abort(422)

            # Pulling information from data body into respective variables
            category = body.get('quiz_category')
            previous_questions = body.get('previous_questions')

            # Defining behavior for what to return based on where a user is at
            # in their quiz
            if category['type'] == 'click':
                available_questions = Question.query.filter(
                    Question.id.notin_((previous_questions))).all()
            else:
                available_questions = Question.query.filter_by(
                    category=category['id']).filter(
                    Question.id.notin_(
                        (previous_questions))).all()

            # Getting random question from list of available_questions
            new_question = available_questions[random.randrange(
                0, len(available_questions))].format() if len(available_questions) > 0 else None

            # Returning successful information
            return jsonify({
                'success': True,
                'question': new_question
            })
        # Handling error scenarios
        except BaseException:
            abort(422)

    # ERROR SCENARIO HANDLING
    # ---------------------------------------------------------------------------
    # Creating error handler for 400 errors
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad request'
        }), 400

    # Creating error handler for 404 errors
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Resource not found'
        }), 404

    # Creating error handler for 422 errors
    @app.errorhandler(422)
    def unable_to_process(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unable to process request'
        }), 422

    return app
