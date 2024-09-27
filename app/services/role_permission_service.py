from app.models.role_permission_model import role_permission_table
from botocore.exceptions import ClientError
import uuid


def assign_permissions_to_role(role_id, permission_id):
    role_permission_id = str(uuid.uuid4())
    item = {
        'RolePermissionId': role_permission_id,
        'roleId': role_id,
        'permissionId': permission_id
    }
    try:
        role_permission_table.put_item(Item=item)
        return item
    except ClientError as e:
        print(f"Error assigning permission to role: {str(e)}")
        return None

def get_permissions_for_role(role_id):
    try:
        response = role_permission_table.scan(
            FilterExpression='roleId = :roleId',
            ExpressionAttributeValues={':roleId': role_id}
        )
        return response.get('Items', [])
    except ClientError as e:
        print(f"Error getting permissions for role: {str(e)}")
        return []

def remove_permission_from_role(role_permission_id):
    try:
        response = role_permission_table.delete_item(
            Key={'RolePermissionId': role_permission_id},
            ReturnValues="ALL_OLD"
        )
        return response.get('Attributes')
    except ClientError as e:
        print(f"Error removing permission from role: {str(e)}")
        return None

    