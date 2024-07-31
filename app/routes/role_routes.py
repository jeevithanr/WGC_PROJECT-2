from flask import request
from app.services.role_service import create_role, get_role, get_all_roles, update_role, delete_role

def init_role_routes(app):
    @app.route('/create_role', methods=['POST'])
    def create_role_route():
        data = request.get_json()
        return create_role(data)

    @app.route('/get_role/<string:roleId>', methods=['GET'])
    def get_role_route(roleId):
        return get_role(roleId)

    @app.route('/get_all_roles', methods=['GET'])
    def get_all_roles_route():
        return get_all_roles()

    @app.route('/update_role/<string:roleId>', methods=['PUT'])
    def update_role_route(roleId):
        data = request.get_json()
        return update_role(roleId, data)

    @app.route('/delete_role/<string:roleId>', methods=['DELETE'])
    def delete_role_route(roleId):
        return delete_role(roleId)
