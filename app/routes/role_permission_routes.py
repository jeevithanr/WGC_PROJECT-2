from flask import request, jsonify, g
from app.services.role_permission_service import assign_permissions_to_role, get_permissions_for_role, remove_permission_from_role, get_permissions_for_user
from app.utils.jwt_utils import token_required

def init_role_permission_routes(app):
    @app.route('/role-permissions', methods=['POST'])
    def assign_permissions_to_role_route():
        data = request.json
        role_id = data.get('roleId')
        permission_ids = data.get('permissionIds')

        if not isinstance(permission_ids, list):
            return jsonify({'error': 'permissionIds must be a list'}), 400

        result = assign_permissions_to_role(role_id, permission_ids)
        if result:
            return jsonify(result), 201
        return jsonify({'error': 'Failed to assign permissions to role'}), 500

    @app.route('/role-permissions/<role_id>', methods=['GET'])
    @token_required
    def get_permissions_for_role_route(role_id):
        result = get_permissions_for_role(role_id)
        return jsonify(result), 200

    @app.route('/role-permissions/<role_permission_id>', methods=['DELETE'])
    @token_required
    def remove_permission_from_role_route(role_permission_id):
        result = remove_permission_from_role(role_permission_id)
        if result:
            return jsonify({'message': 'Permission removed from role successfully'}), 200
        return jsonify({'error': 'Failed to remove permission from role'}), 500
    
    @app.route('/user-permissions/<user_id>', methods=['GET'])
    def get_permissions_for_user_route(user_id):
        result = get_permissions_for_user(user_id)
        return jsonify(result), 200
