import jwt
from flask import request, jsonify, g
from functools import wraps
from datetime import datetime, timedelta
from config import JWT_ALGORITHM, JWT_SECRET

def encode_auth_token(user_id, role_name):
    try:
        print(f"Encoding JWT for user_id: {user_id}, role_name: {role_name}")
        payload = {
            'exp': datetime.utcnow() + timedelta(days=1),
            'iat': datetime.utcnow(),
            'sub': user_id,
            'role': role_name
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return token.decode('utf-8') if isinstance(token, bytes) else token
    except Exception as e:
        print(f"Error generating JWT Token: {str(e)}")
        return str(e)

def decode_auth_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception('Token has expired')
    except jwt.InvalidTokenError:
        raise Exception('Invalid token')

def token_required(f):
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
        g.user_role = decoded_token.get('role')

        return f(*args, **kwargs)

    return decorated_function

def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return jsonify({'error': 'Authorization token is missing'}), 401

            try:
                token = auth_header.split(" ")[1]
                decoded_token = decode_auth_token(token)
                user_role = decoded_token.get('role')

                if user_role != required_role:
                    return jsonify({'error': 'Access denied'}), 403
                
                g.user_id = decoded_token.get('sub')
                g.user_role = user_role
                
                return f(*args, **kwargs)
            except IndexError:
                return jsonify({'error': 'Bearer token malformed!'}), 401
            except Exception as e:
                return jsonify({'error': str(e)}), 401
        
        return wrapper
    return decorator

