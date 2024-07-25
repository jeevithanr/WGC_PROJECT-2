import boto3
from config import AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION, USER_TABLE

dynamodb = boto3.resource(
    'dynamodb',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)

def create_table_if_not_exists(table_name, key_schema, attribute_definitions):
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=key_schema,
            AttributeDefinitions=attribute_definitions,
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        table.wait_until_exists()
        return table
    except dynamodb.meta.client.exceptions.ResourceInUseException:
        return dynamodb.Table(table_name)

# User Table
user_table = create_table_if_not_exists(
    USER_TABLE,
    [{'AttributeName': 'id', 'KeyType': 'HASH'}],
    [{'AttributeName': 'id', 'AttributeType': 'S'}]
)

