import smtplib
from email.mime.text import MIMEText
from config import SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD

def send_otp_email(email, otp):
    try:
        msg = MIMEText(f"Your OTP for password reset is: {otp}")
        msg['Subject'] = 'Password Reset OTP'
        msg['From'] = SMTP_USERNAME
        msg['To'] = email

        with smtplib.SMTP(SMTP_SERVER,SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(msg['From'], msg['To'], msg.as_string())
    except Exception as e:
        raise Exception(f"Failed to send OTP: {str(e)}")
