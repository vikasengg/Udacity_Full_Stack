import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE 
    end = start + QUESTIONS_PER_PAGE 

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    # @app.route("/api/v1/users")
    # def say_hello():
    #     return jsonify('Hello World')

    # CORS Headers
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization,true")
        response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def retrieve_categories():
        categories = Category.query.order_by(Category.id).all()
        # categories = [category.format() for category in selection]  

        return jsonify ({
            'success': True,
            'categories': {category.id: category.type for category in categories}
            })
    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route('/questions')
    def retrieve_questions():

        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        categories = Category.query.order_by(Category.id).all()
        # categories = [category.format() for category in selection]  

        if len(current_questions) == 0:
            abort(404)
        
        return jsonify ({
            'success': True,
            'questions': current_questions,
            'total_questions': len(Question.query.all()), 
            # 'current_category': None, 
            'categories': {category.id: category.type for category in categories}
            })
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.


    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question=Question.query.filter(question_id.id==question_id).one_or_none()
            if question is None:
                abort(404)

            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            categories = Category.query.order_by(Category.id).all()

            if len(current_questions) == 0:
                abort(404)
            
            # return jsonify ({
            #     'success': True
            #     # 'deleted': question_id
            #     })
            return jsonify ({
                'success': True,
                'questions': current_questions,
                'total_questions': len(Question.query.all()), 
                # 'current_category': None, 
                'categories': {category.id: category.type for category in categories}
                })
        except Exception as e:
            print(e)
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route("/questions", methods=["POST"])
    def create_question():
        body = request.get_json()
        new_question = body.get("question", None)
        new_answer = body.get("answer",None)
        new_difficulty = body.get("difficulty", None)
        new_category = body.get("category", None)

        try:
            question = Question(question=new_question,answer=new_answer,difficulty=new_difficulty,category=new_category)
            question.insert()

            selection = Question.query.order_by(Question.id).all()
            current_question=paginate_questions(request,selection)

            if len(current_question) == 0:
                abort(404)
        
            return jsonify ({
            'success': True,
            'created': question.id,
            'question': current_question,
            'total_questions': len(Question.query.all())            
            })
        except:
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route("/questions/search", methods=["POST"])
    def search_question():
        body = request.get_json()
        search_term = body.get("searchTerm", None)

        try:
            selection = Question.query.order_by(Question.id).filter(Question.question.ilike( (f'%{search_term}%')).all())
            current_questions = paginate_questions(request, selection)

            return jsonify(
                {
                    "success": True,
                    "questions": current_questions,
                    "total_questions": len(selection),
                    "current_category": None  
                }
            )
        except:
            abort(422)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route("/categories/<int:category_id>/questions", methods=["GET"])
    def get_questions(category_id):

        selection = Question.query.order_by(Question.id).filter(Question.category == category_id)

        try:
            current_questions=paginate_questions(request,selection)
            current_category= Category.query.filter(Category.id == category_id)
            if len(current_questions) == 0:
                abort(404)
        
            return jsonify ({
            'success': True,
            'questions': current_questions,
            'total_questions': len(current_questions),
            'current_category': [category.type.format() for category in current_category]           
            })
        except:
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def start_quiz():
        try:
            body = request.get_json()
            category = body.get('quiz_category')
            previous_questions = body.get('previous_questions')
            category_id = category['id']

            if category_id == 0: 
                new_questions = Question.query.filter(Question.id.notin_(previous_questions)).all()
            else: 
                new_questions = Question.query.filter(Question.id.notin_(previous_questions), 
                Question.category == category_id).all()

            question = None
            if(new_questions):
                question = random.choice(new_questions)

            return jsonify({
                'success': True,
                'question': question.format()
            })
        except:
            abort(422)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    return app