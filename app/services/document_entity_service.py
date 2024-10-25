import uuid
from botocore.exceptions import ClientError
from http import HTTPStatus
from app.models.document_entity_model import document_entity_table
from app.enum.document_entity_enum import DocumentEntity
from datetime import datetime
from email.utils import format_datetime
from boto3.dynamodb.conditions import Attr  # type: ignore

def get_document_entity_id(document_type):
    try:
        return DocumentEntity[document_type].value
    except KeyError:
        print(f"Document type '{document_type}' not found in DocumentEntity.")
        return None

def add_document_entity(counselor_id, document_type, file_url,filename,user_id):
    document_id = str(uuid.uuid4())
    entity_id = get_document_entity_id(document_type)

    if entity_id is None:
        print(f"Invalid document type: {document_type}")
        return False

    document_entry = {
        'documentId': document_id,
        'counselorId': counselor_id,
        'documentType': document_type,
        'entityId': entity_id,
        'fileUrl': file_url,
        'filename': filename,  
        'user_id': user_id,
        'created_by': user_id, 
        'created_at': format_datetime(datetime.now()),
        'updated_by': user_id, 
        'updated_at': format_datetime(datetime.now()),
        'deletedAt': None,
        'deletedBy': None    
    }

    try:
        document_entity_table.put_item(Item=document_entry)
        return True
    except Exception as e:
        print(f"Error adding document entity: {e}")
        return False

def get_all_documents():
    try:
        response =  document_entity_table.scan() 
        documents = response.get('Items', [])
        
        if not documents:
            response_data= {
                'success': True,
                'message': 'No documents found.',
                'totalresult': [],
                'statusCode': HTTPStatus.OK.value
            }

        response_data= {
            'success': True,
            'message': 'Documents retrieved successfully.',
            'totalresult': documents,
            'statusCode': HTTPStatus.OK.value
        }

    except ClientError as e:
        response_data = {
            'success': False,
            'message': f'Error retrieving documents: {str(e)}',
            'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR.value
        }

    except Exception as e:
        response_data= {
            'success': False,
            'message': f'Unexpected error occurred: {str(e)}',
            'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR.value
        }
    return response_data

def get_document_by_id(document_id):
    try:
        response =  document_entity_table.get_item(Key={'documentId': document_id})  
        document = response.get('Item')

        if not document:
            response_data= {
                'success': False,
                'message': 'Document not found.',
                'statusCode': HTTPStatus.NOT_FOUND.value
            }

        response_data= {
            'success': True,
            'message': 'Document retrieved successfully.',
            'totalresult': document,
            'statusCode': HTTPStatus.OK.value
        }

    except ClientError as e:
        response_data= {
            'success': False,
            'message': f'Error retrieving document: {str(e)}',
            'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR.value
        }

    except Exception as e:
        response_data = {
            'success': False,
            'message': f'Unexpected error occurred: {str(e)}',
            'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR.value
        }
    return response_data
    
def update_document_entity(counselor_id, filename, file_url, document_type, user_id):
    
    try:
        response = document_entity_table.scan()  
        items = response.get('Items', [])
        matching_item = None
        
        for item in items:
            if item.get('counselorId') == counselor_id and item.get('documentType') == document_type:
                matching_item = item
                break

        if not matching_item:
            print(f"Document entity not found for counselor {counselor_id} and type {document_type}.")
            return {
                'success': False,
                'message': f'Document entity not found for counselor {counselor_id} and type {document_type}.',
                'statusCode': HTTPStatus.NOT_FOUND.value
            }
        document_entity_table.update_item(
            Key={'documentId': matching_item['documentId']}, 
            UpdateExpression="SET filename = :filename, fileUrl = :fileUrl, updated_by = :updated_by, updated_at = :updated_at",
            ExpressionAttributeValues={
                ':filename': filename,  
                ':fileUrl': file_url,   
                ':updated_by': user_id,  
                ':updated_at': datetime.now().isoformat() 
            }
        )
        print(f"Document entity for {document_type} updated successfully for counselor {counselor_id}")

        response_data = {
            'success': True,
            'message': f'{document_type} document entity updated successfully',
            'statusCode': HTTPStatus.OK.value
        }

    except Exception as e:
        print(f"Error updating document entity: {e}")
        response_data = {
            'success': False,
            'message': f'Error updating document entity: {e}',
            'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR.value
        }

    return response_data

def delete_documents(counselor_id, user_id):
    try:
        response = document_entity_table.scan(
            FilterExpression=Attr('counselorId').eq(counselor_id)
        )
        documents = response.get('Items', [])

        if not documents:
            response_data = {
                'success': True,
                'message': 'No documents found for this counselor.',
                'statusCode': HTTPStatus.OK.value
            }

        for document in documents:
            document_id = document['documentId']
            document_entity_table.update_item(
                Key={'documentId': document_id},
                UpdateExpression="SET isActive = :isActive, deleted_by = :deleted_by, deletedAt = :deleted_at",
                ExpressionAttributeValues={
                    ':isActive': False,
                    ':deleted_by': user_id,
                    ':deleted_at': format_datetime(datetime.now())
                }
            )

        response_data = {
            'success': True,
            'message': 'Documents soft deleted successfully.',
            'statusCode': HTTPStatus.OK.value,
            'total_deleted': len(documents)
        }

    except ClientError as e:
        response_data=  {
            'success': False,
            'message': f'Error soft deleting documents: {str(e)}',
            'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR.value
        }
    except Exception as e:
        response_data = {
            'success': False,
            'message': f'Unexpected error occurred: {str(e)}',
            'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR.value
        }
    return response_data
