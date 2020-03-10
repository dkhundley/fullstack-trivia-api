import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    # GET Tests
    # --------------------------------------------------------------------------
    # Creating test for GET categories endpoint
    def test_get_categories_basic(self):
        # Getting result from endpoint
        res = self.client().get('/categories')
        # Transforming response into JSON
        data = json.loads(res.data)

        # Ensuring data passes tests as defined below
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))

    # Creating test for GET categories when category_id doesn't exist
    def test_get_categories_nonexistent(self):
        # Attempting to get high value, likely non-existent result
        res = self.client().get('/categories/100000')
        # Transforming response into JSON
        data = json.loads(res.data)

        # Ensuring data passes tests as defined below
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    # Creating test for GET questions endpoint
    def test_get_questions_basic(self):
        # Getting result from endpoint
        res = self.client().get('/questions')
        # Transforming response into JSON
        data = json.loads(res.data)

        # Ensuring data passes tests as defined below
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['total_questions']))
        self.assertTrue(len(data['categories']))

    # Creating test for GET questions endpoint when pagination set too high
    def test_get_questions_high_pagination(self):
        # Attempting to get result from endpoint with high pagination
        res = self.client().get('/questions?page=100000')
        # Transforming response into JSON
        data = json.loads(res.data)

        # Ensuring data passes tests as defined below
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')



    # DELETE Tests
    # --------------------------------------------------------------------------
    # Creating test of delete functionality from DELETE endpoint
    def test_delete_question_basic(self):
        # Creating a dummy question
        dummy_question = Question(question = 'What is your quest?',
                                  answer = 'To seek the Holy Grail!',
                                  difficulty = 1,
                                  category = 1)

        # Adding dummy question to database
        dummy_question.insert()

        # Collecting ID from newly inserted question
        dummy_question_id = dummy_question.id

        # Attempting to delete dummy question
        res = self.client().delete('/questions/{}'.format(dummy_question_id))
        # Transforming response into JSON
        data = json.loads(res.data)

        # Ensuring data passes tests as defined below
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], str(dummy_question_id))

    # Creating a test to see if the appropriate error is thrown when unexpected DELETE request is passed
    def test_delete_question_422(self):
        # Attempting to delete a question with a bad request
        res = self.client().delete('/questions/asdkfjaskf')
        # Transforming data into JSON
        data = json.loads(res.data)

        # Ensuring data passes tests as defined below
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unable to process request')



    # POST Tests
    # --------------------------------------------------------------------------


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
