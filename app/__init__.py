from flask import Flask
from flask_cors import CORS
from app.routes.user_routes import init_user_routes
from app.routes.students_routes import init_student_routes
from app.routes.role_routes import init_role_routes
from app.routes.auth_routes import init_auth_routes
from app.routes.role_permission_routes import init_role_permission_routes
from app.routes.permissions_routes import init_permissions_routes

def create_app():
    app = Flask(__name__)
    CORS(app)
    init_user_routes(app)
    init_student_routes(app)
    init_role_routes(app)
    init_auth_routes(app)
    init_permissions_routes(app)
    init_role_permission_routes(app)
    return app
