from app.utils.dynamodb_utils import create_table_if_not_exists
from config import ROLE_TABLE

# Role Table
role_table = create_table_if_not_exists(
    ROLE_TABLE,
    [{'AttributeName': 'roleId', 'KeyType': 'HASH'}],
    [{'AttributeName': 'roleId', 'AttributeType': 'S'}]
)
