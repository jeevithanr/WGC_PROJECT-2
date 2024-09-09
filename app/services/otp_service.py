import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from app.models.user_model import user_table
from botocore.exceptions import ClientError
from flask import jsonify
from config import SMTP_SERVER, SMTP_PASSWORD, SMTP_PORT, SMTP_USERNAME


def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email(email, otp):
    subject = "Password Reset OTP"
    body = f"Your OTP for password reset is: {otp}. This OTP will expire in 10 minutes."

    message = MIMEMultipart()
    message["From"] = SMTP_USERNAME
    message["To"] = email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(message)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def create_otp_for_user(email):
    try:
        # Check if the user exists
        response = user_table.scan(
            FilterExpression='email = :email',
            ExpressionAttributeValues={':email': email}
        )
        items = response.get('Items')
        
        if not items:
            return jsonify({'error': 'User not found'}), 404

        user = items[0]
        user_id = user['id']

        # Generate OTP
        otp = generate_otp()

        # Store the OTP in the user's record
        user_table.update_item(
            Key={'id': user_id},
            UpdateExpression='SET resetOTP = :otp, resetOTPExpiry = :expiry',
            ExpressionAttributeValues={
                ':otp': otp,
                ':expiry': (datetime.utcnow() + timedelta(minutes=10)).isoformat()  # OTP expires in 10 minutes
            }
        )

        # Send the OTP email
        if send_otp_email(email, otp):
            return jsonify({'message': 'OTP sent successfully to your email'}), 200
        else:
            return jsonify({'error': 'Failed to send OTP email'}), 500

    except ClientError as e:
        return jsonify({'error': str(e)}), 500

def verify_otp(email, otp):
    try:
        # Find the user with the given email
        response = user_table.scan(
            FilterExpression='email = :email',
            ExpressionAttributeValues={':email': email}
        )
        items = response.get('Items')
        
        if not items:
            return jsonify({'error': 'User not found'}), 404

        user = items[0]
        stored_otp = user.get('resetOTP')
        otp_expiry = user.get('resetOTPExpiry')

        if not stored_otp or not otp_expiry:
            return jsonify({'error': 'No OTP request found'}), 400

        # Check if OTP has expired
        if datetime.utcnow() > datetime.fromisoformat(otp_expiry):
            return jsonify({'error': 'OTP has expired'}), 400

        # Verify OTP
        if otp != stored_otp:
            return jsonify({'error': 'Invalid OTP'}), 400

        return jsonify({'message': 'OTP verified successfully'}), 200

    except ClientError as e:
        return jsonify({'error': str(e)}), 500