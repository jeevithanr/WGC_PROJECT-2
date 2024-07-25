from app.utils.dynamodb_utils import create_table_if_not_exists
from config import STUDENT_TABLE

# Student Table
student_table = create_table_if_not_exists(
    STUDENT_TABLE,
    [{'AttributeName': 'studentId', 'KeyType': 'HASH'}],
    [{'AttributeName': 'studentId', 'AttributeType': 'S'}]
)
