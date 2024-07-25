from app.utils.dynamodb_utils import create_table_if_not_exists
from config import USER_TABLE

# User Table
user_table = create_table_if_not_exists(
    USER_TABLE,
    [{'AttributeName': 'id', 'KeyType': 'HASH'}],
    [{'AttributeName': 'id', 'AttributeType': 'S'}]
)
