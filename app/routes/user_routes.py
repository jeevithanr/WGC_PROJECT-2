from flask import request
from app.services.user_service import add_user, get_user, update_user, delete_user, get_all_users

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
    def get_all_users_route():
        return get_all_users()
