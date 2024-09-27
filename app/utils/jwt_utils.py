import jwt
from flask import request, jsonify, g
from functools import wraps
from datetime import datetime, timedelta
from config import JWT_ALGORITHM, JWT_SECRET
from app.services.role_permission_service import get_permissions_for_role
from app.services.permissions_service import get_permission
from app.services.role_service import get_role_by_user_id

def encode_auth_token(user_id):
    #Generate JWT token.
    try:
        print(f"Encoding JWT for user_id: {user_id}")
        payload = {
            'exp': datetime.utcnow() + timedelta(days=1),
            'iat': datetime.utcnow(),
            'sub': user_id
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return token
    except Exception as e:
        print(f"Error generating JWT Token: {str(e)}")
        return str(e)

def decode_auth_token(token):
    #Decode JWT token.
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception('Token has expired')
    except jwt.InvalidTokenError:
        raise Exception('Invalid token')

def token_required(f):
    #Decorator to check for token in request headers.
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Token is missing!'}), 401
        
        try:
            token = auth_header.split(" ")[1]
            decoded_token = decode_auth_token(token)
        except IndexError:
            return jsonify({'error': 'Bearer token malformed!'}), 401
        except Exception as e:
            return jsonify({'error': str(e)}), 401
        
        g.user_id = decoded_token.get('sub')
        return f(*args, **kwargs)

    return decorated_function

def permission_required(permission_name):
    #Decorator to check if the user has the required permission.
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return jsonify({'message': 'Missing token'}), 403

            try:
                token = auth_header.split(" ")[1]
                decoded_token = decode_auth_token(token)
            except IndexError:
                return jsonify({'message': 'Bearer token malformed'}), 403
            except Exception as e:
                return jsonify({'message': str(e)}), 403

            user_id = decoded_token.get('sub')
            if not user_id:
                return jsonify({'message': 'Invalid token'}), 403

            role_id = get_role_by_user_id(user_id)
            if not role_id:
                return jsonify({'message': 'User role not found'}), 403

            permissions = get_permissions_for_role(role_id)
            permission_ids = [perm['permissionId'] for perm in permissions]
            permission_details = [get_permission(perm_id) for perm_id in permission_ids]
            permission_names = [perm['name'] for perm in permission_details if 'name' in perm]

            if permission_name not in permission_names:
                return jsonify({'message': 'Permission denied'}), 403

            return func(*args, **kwargs)
        return wrapper
    return decorator
