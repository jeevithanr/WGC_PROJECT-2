import uuid
from datetime import datetime
from flask import jsonify
from app.models.role_model import role_table

def create_role(data):
    role_id = str(uuid.uuid4())
    role_details = {
        'roleId': role_id,
        'roleName': data.get('roleName'),
        'enabled': data.get('enabled', True),  # Default to True
        'createdDate': datetime.utcnow().isoformat(),
        'updatedDate': '',
        'deletedDate': ''
    }

    try:
        role_table.put_item(Item=role_details)
        return jsonify({'message': 'Role created successfully', 'roleId': role_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_role(roleId):
    try:
        response = role_table.get_item(Key={'roleId': roleId})
        role_details = response.get('Item')

        if role_details:
            return jsonify({
                'success': True,
                'data': role_details,
                'message': 'Role retrieved successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Role not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

def get_all_roles():
    try:
        response = role_table.scan()
        roles = response.get('Items', [])
        return jsonify({
            'success': True,
            'data': roles,
            'message': 'All roles retrieved successfully',
            'count': len(roles)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

def update_role(roleId, data):
    try:
        response = role_table.get_item(Key={'roleId': roleId})
        if 'Item' not in response:
            return jsonify({'error': 'Role not found'}), 404

        update_expression = "set updatedDate = :updatedDate, "
        expression_attribute_values = {":updatedDate": datetime.utcnow().isoformat()}
        for key, value in data.items():
            update_expression += f"{key} = :{key}, "
            expression_attribute_values[f":{key}"] = value

        update_expression = update_expression[:-2]

        role_table.update_item(
            Key={'roleId': roleId},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values
        )
        return jsonify({'message': 'Role updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def delete_role(roleId):
    try:
        response = role_table.get_item(Key={'roleId': roleId})
        if 'Item' not in response:
            return jsonify({'error': 'Role not found'}), 404

        role_table.update_item(
            Key={'roleId': roleId},
            UpdateExpression="set deletedDate = :deletedDate, enabled = :enabled",
            ExpressionAttributeValues={
                ':deletedDate': datetime.utcnow().isoformat(),
                ':enabled': False
            }
        )
        return jsonify({'message': 'Role marked as deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
