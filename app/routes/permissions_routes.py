from flask import request, jsonify
from app.services.permissions_service import create_permission, get_permission, update_permission, delete_permission

def init_permissions_routes(app):
    @app.route('/permissions', methods=['POST'])
    def create_permission_route():
        data = request.json
        result = create_permission(data)
        if result:
            return jsonify(result), 201
        return jsonify({'error': 'Failed to create permission'}), 500

    @app.route('/permissions/<permission_id>', methods=['GET'])
    def get_permission_route(permission_id):
        result = get_permission(permission_id)
        if result:
            return jsonify(result), 200
        return jsonify({'error': 'Permission not found'}), 404

    @app.route('/permissions/<permission_id>', methods=['PUT'])
    def update_permission_route(permission_id):
        data = request.json
        result = update_permission(permission_id, data)
        if result:
            return jsonify(result), 200
        return jsonify({'error': 'Failed to update permission'}), 500

    @app.route('/permissions/<permission_id>', methods=['DELETE'])
    def delete_permission_route(permission_id):
        result = delete_permission(permission_id)
        if result:
            return jsonify({'message': 'Permission deleted successfully'}), 200
        return jsonify({'error': 'Failed to delete permission'}), 500