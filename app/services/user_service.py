from flask import jsonify, request
import uuid
from botocore.exceptions import ClientError
from app.models.user_model import user_table


def add_user(data):
    
    id = str(uuid.uuid4())
    firstname = data.get('firstname')
    lastname = data.get('lastname')
    email = data.get('email')
    contactNo = data.get('contactNo')
    country = data.get('country')
    timezone = data.get('timezone')

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
                'timezone': timezone
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
        return jsonify({'success': True, 'data': item}), 200
    except ClientError as e:
        return jsonify({'error': str(e)}), 500

def update_user(id):
    data = request.get_json()
    update_expression = "SET "
    expression_attribute_values = {}

    for key, value in data.items():
        update_expression += f"{key} = :{key}, "
        expression_attribute_values[f":{key}"] = value

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
    try:
        user_table.delete_item(Key={'id': id})
        return jsonify({'message': 'User deleted successfully'}), 200
    except ClientError as e:
        return jsonify({'error': str(e)}), 500

def get_all_users():
    try:
        response = user_table.scan()
        items = response.get('Items', [])

        result = {
            "success": True,
            "count": len(items),
            "data": items
        }

        return jsonify(result), 200
    except ClientError as e:
        return jsonify({'error': str(e)}), 500
