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

      # Handling 404 error issues if valid
      if not categories:
          abort(404)
      # Returning proper response
      else:
          return jsonify({
            'success': True,
            'catgories': {category.id: category.type for category in categories}
          })

  # Defining endpoint to handle GET requests for questions and correlated categoiry
  @app.endpoint('/questions', methods = ['GET'])
  def get_questions():
      # Querying questions ordered by ID using SQLAlchemy
      questions = Question.query.order_by(Question.id).all()
      # Paginating questions with helper method
      paginated_questions = paginate_questions(request, questions)

      # Querying categories ored by type using SQLAlchemy
      cateories = Category.query.order_by(Category.type).all()


      # Handling 404 error issues if valid
      if not paginated_questions:
          abort(404)
      # Return valid information
      else:
          return jsonify({
            'success': True,
            'questions': paginated_questions,
            'catgories': {category.id: category.type for category in categories},
            'current_category': None
          })

  # 'DELETE' ENDPOINT SETUP
  # ---------------------------------------------------------------------------
  # Defining endpoint for deleting a question based on question_id
  @app.endpoint('/questions/<question_id>', methods = ['DELETE'])
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
      except:
          abort(422)
      

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
