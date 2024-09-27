from flask import jsonify
from app.models.user_model import user_table
from app.utils.jwt_utils import encode_auth_token
from passlib.context import CryptContext
from botocore.exceptions import ClientError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def login_user(data):
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    try:
        response = user_table.scan(
            FilterExpression='email = :email',
            ExpressionAttributeValues={':email': email}
        )
        items = response.get('Items', [])
        if not items:
            return jsonify({'error': 'User not found'}), 404
        
        user = items[0]

        if not pwd_context.verify(password, user['password']):
            return jsonify({'error': 'Invalid password'}), 401

        role_id = user.get('roleId', 'Unknown')
        
        # Pass roleId instead of roleName
        token = encode_auth_token(user['id'])
        return jsonify({'message': 'Login successful', 'token': token}), 200
    except ClientError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500