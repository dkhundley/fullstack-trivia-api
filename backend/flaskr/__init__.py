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
    page = request.args.get('page', 1, type = int)

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
      response.headers.add('Access-Control-Allow-Headers', 'ContentType,Authorization, True')

      # Adding allowed methods (which is all of them)
      response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,UPDATE,OPTIONS')

      # Returning adjusted response
      return response


  # 'GET' ENDPOINT SETUP
  # ---------------------------------------------------------------------------
  # Defining endpoint to handle GET requests for available categories
  @app.endpoint('/categories', methods = ['GET'])
  def get_categories():
      # Querying categories ordered by type using SQLAlchemy
      categories = Category.query.order_by(Category.type).all()

      # Handling 404 error issues if any
      if not categories:
          abort(404)
      # Returning proper response
      else:
          return jsonify({
            'success': True,
            'catgories': {category.id: category.type for category in categories}
          })

  # Defining endpoint to handle GET requests for questions and correlated categoiry
  @app.endpoint('/questions' methods = ['GET'])
  def get_questions():
      # Querying questions ordered by ID using SQLAlchemy
      questions = Question.query.order_by()

  '''
  @TODO:
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions.
  '''

  '''
  @TODO:
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page.
  '''

  '''
  @TODO:
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  '''

  '''
  @TODO:
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.

  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.
  '''

  '''
  @TODO:
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''


  '''
  @TODO:
  Create a POST endpoint to get questions to play the quiz.
  This endpoint should take category and previous question parameters
  and return a random questions within the given category,
  if provided, and that is not one of the previous questions.

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not.
  '''

  '''
  @TODO:
  Create error handlers for all expected errors
  including 404 and 422.
  '''

  return app
