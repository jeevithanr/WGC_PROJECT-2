from flask import Flask
from app.routes.user_routes import init_user_routes

def create_app():
    app = Flask(__name__)
    init_user_routes(app)
    return app
