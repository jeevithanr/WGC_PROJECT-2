from app.utils.dynamodb_utils import create_table_if_not_exists
from config import PERMISSIONS_TABLE

# Permissions Table
permissions_table = create_table_if_not_exists(
    PERMISSIONS_TABLE,
    [{'AttributeName': 'permissionId', 'KeyType': 'HASH'}],
    [{'AttributeName': 'permissionId', 'AttributeType': 'S'}]
)
