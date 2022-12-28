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
        self.database_path = "postgres://{}/{}".format('postgres:postgres@localhost:5432', self.database_name)
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

    def test_get_categories_success(self):
        endpoint = "/categories"

        response = self.client().get(endpoint)
        data = json.loads(response.data)

        self.assertTrue(response.status_code == 200)
        self.assertTrue(data['categories'])
        self.assertTrue(len(data['categories']) > 0)

    def test_get_categories_fail(self):
        endpoint = "/categories"

        response = self.client().post(endpoint)

        self.assertTrue(response.status_code == 405)

    def test_get_questions_success(self):
        endpoint = "/questions?page=1"

        response = self.client().get(endpoint)
        data = json.loads(response.data)

        self.assertTrue(response.status_code == 200)
        self.assertTrue(data['questions'])
        self.assertTrue(len(data['questions']) > 0)

    def test_delete_question_success(self):
        endpoint = "/questions/1"

        response = self.client().delete(endpoint)
        data = json.loads(response.data)

        self.assertTrue(response.status_code == 200)

    def test_delete_question_fail(self):
        endpoint = "/questions/999999999"

        response = self.client().delete(endpoint)
        data = json.loads(response.data)

        self.assertTrue(response.status_code == 404)

    def test_question_post_success(self):
        endpoint = "/questions"

        request = {
            "question": "New Question",
            "answer": "Answer",
            "difficulty": 1,
            "category": 1
        }

        response = self.client().post(endpoint, json=request)
        data = json.loads(response.data)

        self.assertTrue(response.status_code == 200)

    def test_question_post_search_success(self):
        endpoint = "/questions"

        request = {
            "searchTerm": "boxer"
        }

        response = self.client().post(endpoint, json=request)
        data = json.loads(response.data)

        self.assertTrue(response.status_code == 200)
        self.assertTrue(data['totalQuestions'] > 0)

    def test_get_questions_category_success(self):
        endpoint = "/categories/1/questions"

        response = self.client().get(endpoint)
        data = json.loads(response.data)

        self.assertTrue(response.status_code == 200)
        self.assertTrue(data['totalQuestions'] > 0)

    def test_play_quiz_success(self):
        endpoint = "/quizzes"

        request = {
            'previous_questions': [],
            'quiz_category': 0
        }

        response = self.client().post(endpoint, json=request)
        data = json.loads(response.data)

        self.assertTrue(response.status_code == 200)
        self.assertTrue(data['question'])
  

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()