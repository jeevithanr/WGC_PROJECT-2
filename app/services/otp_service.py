import random
import string
from datetime import datetime, timedelta
from app.utils.email_utils import send_otp_email
from app.models.otp_model import otp_table
from app.services.user_service import update_password,get_user_id_by_email

def generate_otp(length=6):
    digits = string.digits
    otp = ''.join(random.choice(digits) for _ in range(length))
    return otp

def store_otp(email, otp):
    expiration = datetime.utcnow() + timedelta(minutes=10)  # OTP valid for 10 minutes
    otp_table.put_item(Item={
        'email': email,
        'otp': otp,
        'expires_at': expiration.isoformat()
    })

def verify_otp(email, otp):
    response = otp_table.get_item(Key={'email': email})
    otp_record = response.get('Item')
    if not otp_record:
        return False
    if otp != otp_record['otp']:
        return False
    if datetime.utcnow() > datetime.fromisoformat(otp_record['expires_at']):
        return False
    return True

def handle_otp_request(email):
    user_id = get_user_id_by_email(email)
    if not user_id:
        return {'error': 'Email not registered'}, 404

    otp = generate_otp()
    store_otp(email, otp)
    send_otp_email(email, otp)
    return {'message': 'OTP sent to your email'}, 200

def handle_password_reset(email, otp, new_password):
    if not verify_otp(email, otp):
        return {'error': 'Invalid or expired OTP'}, 400

    update_password(email, new_password)
    return {'message': 'Password reset successfully'}, 200

