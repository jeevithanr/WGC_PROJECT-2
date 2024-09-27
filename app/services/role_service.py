import uuid
from datetime import datetime, timezone
from flask import jsonify
from app.models.role_model import role_table
from http import HTTPStatus as StatusCode
from app.models.user_model import user_table

def create_role(data):
    # Generate a unique role ID and insert role details into the database
    role_id = str(uuid.uuid4())
    current_time = datetime.now(timezone.utc)
    formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
    role_details = {
        'roleId': role_id,
        'roleName': data['roleName'],
        'isActive': data.get('isActive', True),
        'createdDate': formatted_time,
        'updatedDate': formatted_time,
        'deletedDate': None
    }

    try:
        role_table.put_item(Item=role_details)
        response_data = {
            'message': 'Role created successfully',
            'roleId': role_id,
            'statusCode': StatusCode.CREATED.value
        }
        return jsonify(response_data), StatusCode.CREATED.value
    except Exception as e:
        response_data = {
            'error': str(e),
            'statusCode': StatusCode.INTERNAL_SERVER_ERROR.value
        }
        return jsonify(response_data), StatusCode.INTERNAL_SERVER_ERROR.value

def get_role(roleId):
    # Retrieve a specific role by its ID
    try:
        response = role_table.get_item(Key={'roleId': roleId})
        role_details = response.get('Item')

        if role_details:
            response_data = {
                'success': True,
                'data': role_details,
                'message': 'Role retrieved successfully',
                'statusCode': StatusCode.OK.value
            }
            return jsonify(response_data), StatusCode.OK.value
        else:
            response_data = {
                'success': False,
                'message': 'Role not found',
                'statusCode': StatusCode.NOT_FOUND.value
            }
            return jsonify(response_data), StatusCode.NOT_FOUND.value
    except Exception as e:
        response_data = {
            'success': False,
            'message': str(e),
            'statusCode': StatusCode.INTERNAL_SERVER_ERROR.value
        }
        return jsonify(response_data), StatusCode.INTERNAL_SERVER_ERROR.value

def get_all_roles():
    # Retrieve all roles from the database
    try:
        response = role_table.scan()
        roles = response.get('Items', [])
        response_data = {
            'success': True,
            'message': 'All roles retrieved successfully',
            'count': len(roles),
            'totalresult': roles,
            'statusCode': StatusCode.OK.value
        }
        return jsonify(response_data), StatusCode.OK.value
    except Exception as e:
        response_data = {
            'success': False,
            'message': str(e),
            'statusCode': StatusCode.INTERNAL_SERVER_ERROR.value
        }
        return jsonify(response_data), StatusCode.INTERNAL_SERVER_ERROR.value

def update_role(roleId, data):
     # Update an existing role's details
    try:
        response = role_table.get_item(Key={'roleId': roleId})
        if 'Item' not in response:
            response_data = {
                'error': 'Role not found',
                'statusCode': StatusCode.NOT_FOUND.value
            }
            return jsonify(response_data), StatusCode.NOT_FOUND.value

        update_expression = "set updatedDate = :updatedDate, "
        expression_attribute_values = {":updatedDate": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}
        for key, value in data.items():
            update_expression += f"{key} = :{key}, "
            expression_attribute_values[f":{key}"] = value

        update_expression = update_expression.rstrip(', ')

        role_table.update_item(
            Key={'roleId': roleId},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values
        )
        response_data = {
            'message': 'Role updated successfully',
            'statusCode': StatusCode.OK.value
        }
        return jsonify(response_data), StatusCode.OK.value
    except Exception as e:
        response_data = {
            'error': str(e),
            'statusCode': StatusCode.INTERNAL_SERVER_ERROR.value
        }
        return jsonify(response_data), StatusCode.INTERNAL_SERVER_ERROR.value

def delete_role(roleId):
    # Mark a role as deleted
    try:
        response = role_table.get_item(Key={'roleId': roleId})
        if 'Item' not in response:
            response_data = {
                'error': 'Role not found',
                'statusCode': StatusCode.NOT_FOUND.value
            }
            return jsonify(response_data), StatusCode.NOT_FOUND.value

        role_table.update_item(
            Key={'roleId': roleId},
            UpdateExpression="set deletedDate = :deletedDate, isActive = :isActive",
            ExpressionAttributeValues={
                ':deletedDate': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
                ':isActive': False
            }
        )
        response_data = {
            'message': 'Role marked as deleted successfully',
            'statusCode': StatusCode.OK.value
        }
        return jsonify(response_data), StatusCode.OK.value
    except Exception as e:
        response_data = {
            'error': str(e),
            'statusCode': StatusCode.INTERNAL_SERVER_ERROR.value
        }
        return jsonify(response_data), StatusCode.INTERNAL_SERVER_ERROR.value

def get_role_by_user_id(user_id):
    try:
        response = user_table.get_item(Key={'id': user_id})
        user = response.get('Item')
        if user:
            role_id = user.get('roleId')
            return role_id
        return None
    except Exception as e:
        print(f"Error getting role by user ID: {str(e)}")
        return None
