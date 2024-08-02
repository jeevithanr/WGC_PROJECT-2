from flask import jsonify, request, g
import uuid
from botocore.exceptions import ClientError
from app.models.user_model import user_table
from app.models.role_model import role_table 

DEFAULT_STUDENT_ROLE_ID = 'e43fd12a-8833-4f62-bbbf-29d6299d8a4f' 

def add_user(data):
    
    id = str(uuid.uuid4())
    firstname = data.get('firstname')
    lastname = data.get('lastname')
    email = data.get('email')
    contactNo = data.get('contactNo')
    country = data.get('country')
    timezone = data.get('timezone')
    roleId = data.get('roleId', DEFAULT_STUDENT_ROLE_ID)
    createdBy = getattr(g, 'user_id', None) 

    if not createdBy:
        createdBy = None

    if not (firstname and lastname and email and contactNo and country and timezone):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        user_table.put_item(
            Item={
                'id': id,
                'firstname': firstname,
                'lastname': lastname,
                'email': email,
                'contactNo': contactNo,
                'country': country,
                'timezone': timezone,
                'roleId': roleId,
                'createdBy': createdBy,
                'updatedBy': None,
                'deletedBy': None
            }
        )
        return jsonify({'message': 'User added successfully', 'id': id}), 201
    except ClientError as e:
        return jsonify({'error': str(e)}), 500

def get_user(id):
    try:
        response = user_table.get_item(Key={'id': id})
        item = response.get('Item')
        if not item:
            return jsonify({'error': 'User not found'}), 404

        item = format_user_details(item)

        return jsonify({'success': True, 'data': item}), 200
    except ClientError as e:
        return jsonify({'error': str(e)}), 500

def update_user(id):
    data = request.get_json()
    update_expression = "SET "
    expression_attribute_values = {}
    updatedBy = getattr(g, 'user_id', None)

    for key, value in data.items():
        update_expression += f"{key} = :{key}, "
        expression_attribute_values[f":{key}"] = value

    update_expression += "updatedBy = :updatedBy, "
    expression_attribute_values[":updatedBy"] = updatedBy
    update_expression = update_expression.rstrip(", ")

    try:
        user_table.update_item(
            Key={'id': id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values
        )
        return jsonify({'message': 'User updated successfully'}), 200
    except ClientError as e:
        return jsonify({'error': str(e)}), 500

def delete_user(id):
    deletedBy = getattr(g, 'user_id', None)

    if not deletedBy:
        return jsonify({'error': 'User not authenticated'}), 401

    try:
        user_table.update_item(
            Key={'id': id},
            UpdateExpression="SET deletedBy = :deletedBy",
            ExpressionAttributeValues={':deletedBy': deletedBy}
        )
        return jsonify({'message': 'User deleted successfully'}), 200
    except ClientError as e:
        return jsonify({'error': str(e)}), 500

def get_all_users():
    try:
        response = user_table.scan()
        items = response.get('Items', [])

        formatted_items = [format_user_details(item) for item in items]

        result = {
            "success": True,
            "count": len(formatted_items),
            "data": formatted_items
        }

        return jsonify(result), 200
    except ClientError as e:
        return jsonify({'error': str(e)}), 500

def format_user_details(item):
    def get_user_details(user_id):
        try:
            response = user_table.get_item(Key={'id': user_id})
            user = response.get('Item')
            if user:
                return {
                    'id': user.get('id'),
                    'name': f"{user.get('firstname')} {user.get('lastname')}"
                }
            else:
                return {'id': user_id, 'name': 'Unknown'}
        except ClientError:
            return {'id': user_id, 'name': 'Unknown'}

    def get_role_details(role_id):
        try:
            response = role_table.get_item(Key={'roleId': role_id})
            role = response.get('Item')
            if role:
                return {
                    'id': role.get('roleId'),
                    'name': role.get('roleName')
                }
            else:
                return {'id': role_id, 'name': 'Unknown'}
        except ClientError:
            return {'id': role_id, 'name': 'Unknown'}

    if item.get('createdBy'):
        item['createdBy'] = get_user_details(item['createdBy'])
    if item.get('updatedBy'):
        item['updatedBy'] = get_user_details(item['updatedBy'])
    if item.get('deletedBy'):
        item['deletedBy'] = get_user_details(item['deletedBy'])
    if item.get('roleId'):
        item['role'] = get_role_details(item['roleId'])
        del item['roleId']

    return item


