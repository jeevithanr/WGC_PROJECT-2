from flask import jsonify, request, g
import uuid
from passlib.context import CryptContext
from botocore.exceptions import ClientError
from app.models.user_model import user_table
from app.models.role_model import role_table
from datetime import datetime
from app.services.otp_service import create_otp_for_user, verify_otp
from http import HTTPStatus as StatusCode

DEFAULT_STUDENT_ROLE_ID = 'e43fd12a-8833-4f62-bbbf-29d6299d8a4f'

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def add_user(data):
    # Add a new user with the provided data and return success or error message.
    id = str(uuid.uuid4())
    firstname = data['firstname']
    lastname = data['lastname']
    email = data['email']
    contactNo = data['contactNo']
    country = data['country']
    timezone = data['timezone']
    roleId = data['roleId'] if 'roleId' in data else DEFAULT_STUDENT_ROLE_ID
    password = data['password']
    
    createdBy = data['createdBy'] if 'createdBy' in data else None
    if createdBy == "null": 
        createdBy = None

    if createdBy is None:
        createdBy = getattr(g, 'user_id', None)

    if not all([firstname, lastname, email, contactNo, country, timezone, password]):
        return jsonify({'error': 'Missing required fields'}), StatusCode.BAD_REQUEST.value

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
                'deletedDate': None,
                'resetOTP': None,
                'resetOTPExpiry': None
            }
        )
        return jsonify({'message': 'User added successfully', 'id': id}), StatusCode.CREATED.value
    except ClientError as e:
        return jsonify({'error': str(e)}), StatusCode.INTERNAL_SERVER_ERROR.value

def get_user(id):
    # Retrieve a user by their ID, including their role information if available.
    try:
        response = user_table.get_item(Key={'id': id})
        item = response.get('Item')
        if not item:
            return jsonify({'error': 'User not found'}), StatusCode.NOT_FOUND.value
        
        role_id = item.get('roleId')
        if role_id:
            try:
                role_response = role_table.get_item(Key={'roleId': role_id})
                role = role_response.get('Item')
                if role:
                    item['role'] = {
                        'id': role['roleId'],
                        'name': role['roleName']
                    }
                else:
                    item['role'] = {'id': role_id, 'name': 'Unknown'}
            except ClientError:
                item['role'] = {'id': role_id, 'name': 'Unknown'}

        item.pop('roleId', None)

        return jsonify({'success': True, 'data': item}), StatusCode.OK.value
    except ClientError as e:
        return jsonify({'error': str(e)}), StatusCode.INTERNAL_SERVER_ERROR.value

def update_user(id, data):
    # Update user details and track who made the changes.
    user_id = data['user_id']
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
        return jsonify({'message': 'User updated successfully'}), StatusCode.OK.value
    except ClientError as e:
        return jsonify({'error': str(e)}), StatusCode.INTERNAL_SERVER_ERROR.value

def delete_user(id):
    # Mark a user as deleted and record who performed the deletion.
    data = request.get_json()
    deletedBy = data['user_id']

    try:
        user_table.update_item(
            Key={'id': id},
            UpdateExpression="SET deletedBy = :deletedBy, deletedDate = :deletedDate",
            ExpressionAttributeValues={
                ':deletedBy': deletedBy,
                ':deletedDate': datetime.utcnow().isoformat()
            }
        )
        return jsonify({'message': 'User marked as deleted successfully'}), StatusCode.OK.value
    except ClientError as e:
        return jsonify({'error': str(e)}), StatusCode.INTERNAL_SERVER_ERROR.value

def get_all_users():
    # Retrieve all users and include their role information if available.
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
                            'id': role['roleId'],
                            'name': role['roleName']
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
        return jsonify(result), StatusCode.OK.value
    except ClientError as e:
        return jsonify({'error': str(e)}), StatusCode.INTERNAL_SERVER_ERROR.value
    
def get_user_id_by_email(email):
    # Get the user ID based on the provided email address.
    try:
        response = user_table.scan(
            FilterExpression='email = :email',
            ExpressionAttributeValues={':email': email}
        )
        items = response.get('Items')
        if items:
            return items[0]['id']
        return None
    except ClientError as e:
        return None

def update_password(email, new_password):
    # Update the user's password and reset OTP details.
    user_id = get_user_id_by_email(email)
    if not user_id:
        return jsonify({'error': 'User not found'}), StatusCode.NOT_FOUND.value

    hashed_password = pwd_context.hash(new_password)

    try:
        user_table.update_item(
            Key={'id': user_id},
            UpdateExpression='SET password = :password, resetOTP = :otp, resetOTPExpiry = :expiry',
            ExpressionAttributeValues={
                ':password': hashed_password,
                ':otp': None,
                ':expiry': None
            }
        )
        return jsonify({'message': 'Password updated successfully'}), StatusCode.OK.value
    except ClientError as e:
        return jsonify({'error': str(e)}), StatusCode.INTERNAL_SERVER_ERROR.value

def forgot_password(email):
    # Generate and send an OTP for password reset to the provided email.
    return create_otp_for_user(email)

def get_email_by_otp(otp):
    # Retrieve the email associated with the given OTP.
    try:
        response = user_table.scan(
            FilterExpression='resetOTP = :otp',
            ExpressionAttributeValues={':otp': otp}
        )
        items = response.get('Items')
        if items:
            return items[0]['email']
        return None
    except ClientError as e:
        return None

def reset_password(otp, new_password):
    # Verify the OTP and reset the password if the OTP is valid.
    email = get_email_by_otp(otp)
    if not email:
        return jsonify({'error': 'Invalid OTP'}), StatusCode.NOT_FOUND.value

    verification_result, status_code = verify_otp(email, otp)
    if status_code != StatusCode.OK.value:
        return jsonify(verification_result), status_code

    return update_password(email, new_password)