from flask import request, jsonify
from app.services.auth_service import login_user
from app.services.otp_service import handle_otp_request, handle_password_reset

def init_auth_routes(app):
    @app.route('/login', methods=['POST'])
    def login_route():
        data = request.get_json() 
        return login_user(data) 
    
    @app.route('/request_otp', methods=['POST'])
    def request_otp():
        data = request.get_json()
        email = data.get('email')
        response, status_code = handle_otp_request(email)
        return jsonify(response), status_code

    @app.route('/reset_password', methods=['POST'])
    def reset_password_with_otp():
        data = request.get_json()
        email = data.get('email')
        otp = data.get('otp')
        new_password = data.get('new_password')
        response, status_code = handle_password_reset(email, otp, new_password)
        return jsonify(response), status_code