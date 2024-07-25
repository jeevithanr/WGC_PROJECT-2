from flask import Flask
from app.routes.user_routes import init_user_routes
from app.routes.students_routes import init_student_routes

def create_app():
    app = Flask(__name__)
    init_user_routes(app)
    init_student_routes(app)
    return app
