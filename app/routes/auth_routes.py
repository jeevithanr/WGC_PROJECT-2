from flask import request
from app.services.auth_service import login_user

def init_auth_routes(app):
    @app.route('/login', methods=['POST'])
    def login_route():
        data = request.get_json() 
        return login_user(data) 