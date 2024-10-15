from config import COUNSELOR_TABLE
from app.utils.dynamodb_utils import create_table_if_not_exists

counselor_table = create_table_if_not_exists(
    COUNSELOR_TABLE,
    [{ 'AttributeName':'counselorId',
      'KeyType':'HASH'}],
    [{
        'AttributeName':'counselorId',
        'AttributeType':'S'}]
)