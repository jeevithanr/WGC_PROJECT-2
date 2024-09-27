from app.models.permissions_model import permissions_table
from botocore.exceptions import ClientError
import uuid

def create_permission(data):
    permission_id = str(uuid.uuid4())
    item = {
        'permissionId': permission_id,
        'name': data['name'],
        'description': data.get('description', '')
    }
    try:
        permissions_table.put_item(Item=item)
        return item
    except ClientError as e:
        print(f"Error creating permission: {str(e)}")
        return None

def get_permission(permission_id):
    try:
        response = permissions_table.get_item(Key={'permissionId': permission_id})
        return response.get('Item')
    except ClientError as e:
        print(f"Error getting permission: {str(e)}")
        return None


def update_permission(permission_id, data):
    update_expression = "SET "
    expression_attribute_values = {}
    for key, value in data.items():
        update_expression += f"#{key} = :{key}, "
        expression_attribute_values[f':{key}'] = value
    update_expression = update_expression.rstrip(', ')

    expression_attribute_names = {f'#{key}': key for key in data.keys()}

    try:
        response = permissions_table.update_item(
            Key={'permissionId': permission_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ExpressionAttributeNames=expression_attribute_names,
            ReturnValues="ALL_NEW"
        )
        return response.get('Attributes')
    except ClientError as e:
        print(f"Error updating permission: {str(e)}")
        return None

def delete_permission(permission_id):
    try:
        response = permissions_table.delete_item(
            Key={'permissionId': permission_id},
            ReturnValues="ALL_OLD"
        )
        return response.get('Attributes')
    except ClientError as e:
        print(f"Error deleting permission: {str(e)}")
        return None