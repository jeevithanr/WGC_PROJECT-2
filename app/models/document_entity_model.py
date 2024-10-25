from app.utils.dynamodb_utils import create_table_if_not_exists
from config import DOC_ENTITY_TABLE


document_entity_table = create_table_if_not_exists(
    DOC_ENTITY_TABLE,
    [{'AttributeName': 'documentId', 'KeyType': 'HASH'}],
    [{'AttributeName': 'documentId', 'AttributeType': 'S'}]
)
