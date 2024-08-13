from flask import request,jsonify,g
from app.services.user_service import add_user, get_user, update_user, delete_user, get_all_users
from app.utils.jwt_utils import token_required, role_required


def init_user_routes(app):
    @app.route('/add_user', methods=['POST'])
    def add_user_route():
        data = request.get_json()
        return add_user(data)

    @app.route('/get_user/<string:id>', methods=['GET'])
    def get_user_route(id):
        return get_user(id)

    @app.route('/update_user/<string:id>', methods=['PUT'])
    def update_user_route(id):
        data = request.get_json()
        return update_user(id, data)

    @app.route('/delete_user/<string:id>', methods=['DELETE'])
    def delete_user_route(id):
        return delete_user(id)

    @app.route('/get_all_users', methods=['GET'])
    @token_required
    @role_required('Admin')
    def get_all_users_route():
        return get_all_users()
    
    @app.route('/some_protected_route', methods=['GET'])
    def some_protected_route():
        user_id = g.user_id
        
        user_response = get_user(user_id)
        
        if user_response[1] != 200:
            return user_response
        
        user_data = user_response[0].json['data']
        user_role = user_data.get('role', {}).get('name', 'Unknown')
        
        return jsonify({'message': f'Hello, user {user_id} with role {user_role}'}), 200
