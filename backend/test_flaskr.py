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
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format('student','student','localhost:5432', self.database_name)
        self.app = create_app(self.database_path)
        self.client = self.app.test_client
        # setup_db(self.app, self.database_path)
    
        # # binds the app to the current context
        # with self.app.app_context():
        #     self.db = SQLAlchemy()
        #     self.db.init_app(self.app)
        # #     # create all tables
        #     self.db.create_all()

    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    # Test case for getting the list of categories
    def test_get_categories_all(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["categories"])

    # Test case for invalid operation for categories
    def test_delete_categories_not_allowed(self):
        res = self.client().delete("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], 'method not allowed')

    # Test case for getting the list of questions pagewise
    def test_get_paginated_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(len(data["categories"]))
        self.assertTrue(data["total_questions"])

    # Test case for diplaying the page not found error. 
    def test_404_requesting_beyond_valid_page(self):
        res = self.client().get("/questions?page=1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Page not found")

    # # Test case for creating a question 
    # def test_create_new_question(self):
    #     self.new_question = {"question":"who is the highest individual run scorer in ODI", "answer":"Rohit Sharma", "category":"6", "difficulty":"3"}
    #     res = self.client().post("/questions", json=self.new_question)
    #     data = json.loads(res.data)

    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data["success"], True)
    #     self.assertTrue(data["created"])
    #     self.assertTrue(data["question"])
    #     self.assertTrue(data["total_questions"])

    # # Test case for deleting a question
    # def test_delete_questions(self):
    #     res = self.client().delete("/questions/13")
    #     data = json.loads(res.data)

    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data["success"], True)
    #     self.assertTrue(data["total_questions"])
    #     self.assertTrue(len(data["questions"]))

    # Test case for error while deleting a questions
    def test_422_if_question_does_not_exist(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    # Test case for wild card search for questions
    def test_search_question(self):
        res = self.client().post("/questions/search", json={"searchTerm": "What"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["total_questions"],8)

    # Test case for populating the error if no questions matching the wildcard
    def test_404_search_question_failure(self):
        res = self.client().post("/questions/search", json={"searchTerm": "what and how"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Page not found")


    # Test case for getting the list of questions by Category
    def test_get_paginated_questions_by_category(self):
        res = self.client().get("/categories/5/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])

    # Test case for diplaying the error message when Page number is out of reach while searching questions. 
    def test_404_requesting_beyond_valid_question_by_category(self):
        res = self.client().get("/category/100000/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Page not found")

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()