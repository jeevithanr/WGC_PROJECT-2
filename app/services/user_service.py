from flask import jsonify, request, g
import uuid
from passlib.context import CryptContext
from botocore.exceptions import ClientError
from app.models.user_model import user_table
from app.models.role_model import role_table
from datetime import datetime

DEFAULT_STUDENT_ROLE_ID = 'e43fd12a-8833-4f62-bbbf-29d6299d8a4f'

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def add_user(data):
    id = str(uuid.uuid4())
    firstname = data.get('firstname')
    lastname = data.get('lastname')
    email = data.get('email')
    contactNo = data.get('contactNo')
    country = data.get('country')
    timezone = data.get('timezone')
    roleId = data.get('roleId', DEFAULT_STUDENT_ROLE_ID)
    password = data.get('password')
    
    createdBy = data.get('createdBy')
    if createdBy == "null": 
        createdBy = None

    if createdBy is None:
        createdBy = getattr(g, 'user_id', None)

    if not (firstname and lastname and email and contactNo and country and timezone and password):
        return jsonify({'error': 'Missing required fields'}), 400

    hashed_password = pwd_context.hash(password)

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
                'password': hashed_password,
                'createdBy': createdBy,
                'updatedBy': None,
                'deletedBy': None,
                'createdDate': datetime.utcnow().isoformat(),
                'updatedDate': None,
                'deletedDate': None
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
        
        role_id = item.get('roleId')
        if role_id:
            try:
                role_response = role_table.get_item(Key={'roleId': role_id})
                role = role_response.get('Item')
                if role:
                    item['role'] = {
                        'id': role.get('roleId'),
                        'name': role.get('roleName')
                    }
                else:
                    item['role'] = {'id': role_id, 'name': 'Unknown'}
            except ClientError:
                item['role'] = {'id': role_id, 'name': 'Unknown'}

        item.pop('roleId', None)

        return jsonify({'success': True, 'data': item}), 200
    except ClientError as e:
        return jsonify({'error': str(e)}), 500

def update_user(id, data):
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({'error': 'User ID is required to update the record'}), 400

    update_expression = "SET "
    expression_attribute_values = {}
    
    for key, value in data.items():
        if key != 'user_id':
            update_expression += f"{key} = :{key}, "
            expression_attribute_values[f":{key}"] = value

    update_expression += "updatedBy = :updatedBy, updatedDate = :updatedDate"
    expression_attribute_values[":updatedBy"] = user_id
    expression_attribute_values[":updatedDate"] = datetime.utcnow().isoformat()

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
    data = request.get_json()
    deletedBy = data.get('user_id')

    if not deletedBy:
        return jsonify({'error': 'User ID is required'}), 400

    try:
        user_table.update_item(
            Key={'id': id},
            UpdateExpression="SET deletedBy = :deletedBy, deletedDate = :deletedDate",
            ExpressionAttributeValues={
                ':deletedBy': deletedBy,
                ':deletedDate': datetime.utcnow().isoformat()
            }
        )
        return jsonify({'message': 'User marked as deleted successfully'}), 200
    except ClientError as e:
        return jsonify({'error': str(e)}), 500

def get_all_users():
    try:
        response = user_table.scan()
        items = response.get('Items', [])
        
        for item in items:
            role_id = item.get('roleId')
            if role_id:
                try:
                    role_response = role_table.get_item(Key={'roleId': role_id})
                    role = role_response.get('Item')
                    if role:
                        item['role'] = {
                            'id': role.get('roleId'),
                            'name': role.get('roleName')
                        }
                    else:
                        item['role'] = {'id': role_id, 'name': 'Unknown'}
                except ClientError:
                    item['role'] = {'id': role_id, 'name': 'Unknown'}

            item.pop('roleId', None)        

        result = {
            "success": True,
            "count": len(items),
            "data": items
        }
        return jsonify(result), 200
    except ClientError as e:
        return jsonify({'error': str(e)}), 500
    
def get_user_id_by_email(email):
    response = user_table.scan(
        FilterExpression='email = :email',
        ExpressionAttributeValues={':email': email}
    )
    items = response.get('Items')
    if items:
        return items[0].get('id')
    return None

def update_password(email, new_password):
    user_id = get_user_id_by_email(email)
    if not user_id:
        return {'error': 'User not found'}

    hashed_password = pwd_context.hash(new_password)
    try:
        user_table.update_item(
            Key={'id': user_id},  # Use 'id' as the key attribute
            UpdateExpression='SET password = :password',
            ExpressionAttributeValues={':password': hashed_password}
        )
        return {'message': 'Password updated successfully'}
    except Exception as e:
        return {'error': str(e)}