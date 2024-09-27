from app.utils.dynamodb_utils import create_table_if_not_exists
from config import ROLE_PERMISSION_TABLE

# RolePermission Table
role_permission_table = create_table_if_not_exists(
    ROLE_PERMISSION_TABLE,
    [{'AttributeName': 'RolePermissionId', 'KeyType': 'HASH'}],
    [{'AttributeName': 'RolePermissionId', 'AttributeType': 'S'}] 
)
