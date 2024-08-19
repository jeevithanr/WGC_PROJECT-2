from app.utils.dynamodb_utils import create_table_if_not_exists
from config import OTP_TABLE

# Define OTP Table
otp_table = create_table_if_not_exists(
    OTP_TABLE,
    [{'AttributeName': 'email', 'KeyType': 'HASH'}],
    [{'AttributeName': 'email', 'AttributeType': 'S'}]
)
