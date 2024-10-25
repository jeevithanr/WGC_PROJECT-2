import uuid
import boto3
from flask import jsonify
from botocore.exceptions import ClientError
from email.utils import format_datetime
from app.models.counselor_models import counselor_table  
from app.models.user_model import user_table
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from http import HTTPStatus
from app.services.document_entity_service import add_document_entity,delete_documents,update_document_entity

s3 = boto3.client('s3')
S3_BUCKET = 'wgc-student-bucket-4'  
dynamodb = boto3.resource('dynamodb')

def generate_presigned_url(filename, content_type, folder_name, subfolder):
    try:
        file_key = f"{folder_name}/{subfolder}/{filename}"  
        if filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg'):
            content_type = 'image/jpeg'
        elif filename.lower().endswith('.pdf'):
            content_type = 'application/pdf'
        else:
            content_type = content_type  
        presigned_url = s3.generate_presigned_url(
            ClientMethod='put_object',
            Params={
                'Bucket': S3_BUCKET, 
                'Key': file_key,
                'ContentType': content_type
            },
            ExpiresIn=3600
        )
        return presigned_url, file_key  
    except ClientError as e:
        print(f"Error generating presigned URL: {e}")
        return None, None

def create_counselor(data):
    counselor_id = str(uuid.uuid4())
    firstName = data['firstName']
    lastName = data['lastName']
    gender = data['gender']
    mailid = data['mailid']
    contact_number = data['contact_number']
    alternate_contact_number = data['alternate_contact_number']
    history = data['history']
    experience = data['experience']
    date_of_birth = data['date_of_birth']
    address = data['address']
    country = data['country']
    state = data['state']
    district = data['district']
    city = data['city']
    pincode = data['pincode']
    
    try:
        price = Decimal(data['price']).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) if data.get('price') else Decimal('0.00')
    except (InvalidOperation, ValueError):
        return {
            'success': False,
            'message': 'Invalid price format. Please provide a valid number.',
            'statusCode': HTTPStatus.BAD_REQUEST.value
        }

    specialization = data['specialization']
    qualification = data['qualification']
    language_spoken = data['language_spoken']
    achievements = data['achievements']
    date_of_joining = data['date_of_joining']
    
    try:
        rating = Decimal(data['rating']).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP) if 'rating' in data else Decimal('0.0')
    except (InvalidOperation, ValueError):
        return {
            'success': False,
            'message': 'Invalid rating format. Please provide a valid number.',
            'statusCode': HTTPStatus.BAD_REQUEST.value
        }

    isActive = data.get('isActive', True)
    linkedinURL = data.get('linkedinURL', '')
    availability_status = data['availability_status']

    # Retrieve user_id from the payload
    user_id = data.get('user_id')
    if not user_id:
        return {
            'success': False,
            'message': 'User ID is required.',
            'statusCode': HTTPStatus.BAD_REQUEST.value
        }
    
    photo_name = data.get('PhotoURL', '')  
    resume_file = data.get('resumeURL', '')
    experience_certificate_file = data.get('experience_certificateURL', '')

    created_at = format_datetime(datetime.now())
    updated_at = created_at

    if resume_file and not resume_file.lower().endswith('.pdf'):
        return {
            'success': False,
            'message': 'Resume must be in PDF format.',
            'statusCode': HTTPStatus.BAD_REQUEST.value
        }

    if experience_certificate_file and not experience_certificate_file.lower().endswith('.pdf'):
        return {
            'success': False,
            'message': 'Experience certificate must be in PDF format.',
            'statusCode': HTTPStatus.BAD_REQUEST.value
        }

    # Generate presigned URLs for each file in the respective subfolders
    presigned_url_photo, photo_key = generate_presigned_url(photo_name, 'image/jpeg', counselor_id, 'photo') if photo_name else (None, None)
    presigned_url_resume, resume_key = generate_presigned_url(resume_file, 'application/pdf', counselor_id, 'resume') if resume_file else (None, None)
    presigned_url_cert, cert_key = generate_presigned_url(experience_certificate_file, 'application/pdf', counselor_id, 'exp_certificate') if experience_certificate_file else (None, None)

    # Extract the file name from the file path using string split
    photo_filename = photo_key.split('/')[-1] if photo_key else None
    resume_filename = resume_key.split('/')[-1] if resume_key else None
    cert_filename = cert_key.split('/')[-1] if cert_key else None

    if not presigned_url_photo or (resume_file and not presigned_url_resume) or (experience_certificate_file and not presigned_url_cert):
        return {
            'success': False,
            'message': 'Error generating presigned URL.',
            'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR.value
        }

    if photo_key:
        add_document_entity(counselor_id, 'PHOTO', photo_key, photo_filename,user_id)
    if resume_key:
        add_document_entity(counselor_id, 'RESUME', resume_key, resume_filename,user_id)
    if cert_key:
        add_document_entity(counselor_id, 'EXPERIENCE_CERTIFICATES', cert_key, cert_filename,user_id)

    counselor_details = {
        'counselorId': counselor_id,
        'firstName': firstName,
        'lastName': lastName,
        'gender': gender,
        'mailid': mailid,
        'contact_number': contact_number,
        'alternate_contact_number': alternate_contact_number,
        'history': history,
        'experience': experience,
        'date_of_birth': date_of_birth,
        'address': address,
        'country': country,
        'state': state,
        'district': district,
        'city': city,
        'pincode': pincode,
        'price': price,
        'specialization': specialization,
        'qualification': qualification,
        'language_spoken': language_spoken,
        'achievements': achievements,
        'date_of_joining': date_of_joining,
        'rating': rating,
        'isActive': isActive,
        'linkedinURL': linkedinURL,
        'availability_status': availability_status,
        'PhotoURL': photo_key,  
        'resumeURL': resume_key,  
        'experience_certificateURL': cert_key,  
        'created_by': user_id, 
        'created_at': created_at,
        'updated_by': user_id, 
        'updated_at': updated_at,
        'deletedAt': None,
        'deletedBy': None
    }

    try:
        counselor_table.put_item(Item=counselor_details)

        # Print presigned URLs for reference (or log them)
        print(f"Presigned URL for Photo: {presigned_url_photo}")
        print(f"Presigned URL for Resume: {presigned_url_resume}")
        print(f"Presigned URL for Experience Certificate: {presigned_url_cert}")

        response_data = {
            'success': True,
            'message': 'Counselor created successfully.',
            'totalresult': {
                'counselorId': counselor_id,
                'counselor': counselor_details,
                'presigned_urls': {
                    'photo': presigned_url_photo,
                    'resume': presigned_url_resume,
                    'experience_certificate': presigned_url_cert
                }
            },
            'statusCode': HTTPStatus.CREATED.value
        }
        return response_data

    except ClientError as e:
        return {
            'success': False,
            'message': f'Error creating counselor: {str(e)}',
            'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR.value
        }

    except Exception as e:
        return {
            'success': False,
            'message': f'Unexpected error occurred: {str(e)}',
            'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR.value
        }

def get_all_counselors():
    try:
        response = counselor_table.scan()
        counselors = response.get('Items', [])
        response_data = {
            'success': True,
            'message': 'Counselors retrieved successfully.',
            'count': len(counselors),
            'totalresult': counselors,
            'statusCode': HTTPStatus.OK.value
        }
        return response_data
    except ClientError as e:
        print(f"Error retrieving counselors: {e}")
        response_data = {
            'success': False,
            'message': 'Error retrieving counselors.',
            'totalresult': None,
            'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR.value
        }
        return response_data

def get_counselor_by_id(counselor_id):
    try:
        response = counselor_table.get_item(Key={'counselorId': counselor_id})
        counselor = response.get('Item')
        if counselor:
            response_data = {
                'success': True,
                'message': 'Counselor retrieved successfully.',
                'totalresult': {
                    'counselorId': counselor_id,
                    'counselor': counselor
                },
                'statusCode': HTTPStatus.OK.value
            }
            return response_data
        else:
            response_data = {
                'success': False,
                'message': 'Counselor not found.',
                'statusCode': HTTPStatus.NOT_FOUND.value
            }
            return response_data
    except ClientError as e:
        print(f"Error retrieving counselor: {e}")
        response_data = {
            'success': False,
            'message': 'Error retrieving counselor.',
            'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR.value
        }
        return response_data

def update_counselor(counselor_id, data):
    try:
        # Fetch counselor data
        response = counselor_table.get_item(Key={'counselorId': counselor_id})
        if 'Item' not in response:
            return {
                'success': False,
                'message': 'Counselor not found',
                'statusCode': HTTPStatus.NOT_FOUND.value
            }
        
        counselor = response['Item']
        update_expression = "SET "
        expression_attribute_values = {}
        user_id = data.get('user_id')
        presigned_urls = {}
        updatable_fields = [
            'firstName', 'lastName', 'gender', 'mailid', 'contact_number', 'alternate_contact_number',
            'experience', 'date_of_birth', 'address', 'country', 'state', 'district', 'city', 'pincode',
            'price', 'specialization', 'qualification', 'language_spoken', 'achievements',
            'date_of_joining', 'availability_status'
        ]

        # Update fields if changed
        for field in updatable_fields:
            if field in data and data[field] != counselor.get(field):
                update_expression += f"{field} = :{field}, "
                expression_attribute_values[f":{field}"] = data[field]

        # Handle Price
        if 'price' in data:
            try:
                price_value = Decimal(data['price']).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                if price_value != counselor.get('price'):
                    update_expression += "price = :price, "
                    expression_attribute_values[":price"] = price_value
            except InvalidOperation:
                return {'success': False, 'message': 'Invalid price value', 'statusCode': HTTPStatus.BAD_REQUEST.value}

        # Handle Rating
        if 'rating' in data:
            try:
                rating_value = Decimal(data['rating']).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                if rating_value != counselor.get('rating'):
                    update_expression += "rating = :rating, "
                    expression_attribute_values[":rating"] = rating_value
            except InvalidOperation:
                return {'success': False, 'message': 'Invalid rating value', 'statusCode': HTTPStatus.BAD_REQUEST.value}

        # Handle Photo URL
        if 'PhotoURL' in data:
            old_photo_url = counselor.get('PhotoURL')
            
            if old_photo_url:
                s3.delete_object(Bucket=S3_BUCKET, Key=old_photo_url)
            filekey = data['PhotoURL']
            photo_key = filekey.split('/')[-1]
            presigned_url_photo = generate_presigned_url(photo_key, 'image/jpeg', counselor_id, 'photo')

            if not presigned_url_photo:
                return {'success': False, 'message': 'Error generating presigned URL for Photo', 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR.value}
            update_expression += "PhotoURL = :PhotoURL, "
            expression_attribute_values[':PhotoURL'] = filekey
            presigned_urls['photo'] = presigned_url_photo
            update_document_entity(counselor_id, photo_key, filekey, 'PHOTO', user_id)

        # Handle Resume
        if 'resumeURL' in data:
            old_resume_url = counselor.get('resumeURL')
            if old_resume_url:
                s3.delete_object(Bucket=S3_BUCKET, Key=old_resume_url)
            filekey = data['resumeURL']
            resume_key = filekey.split('/')[-1]
            presigned_url_resume = generate_presigned_url(resume_key, 'application/pdf', counselor_id, 'resume')
            if not presigned_url_resume:
                return {'success': False, 'message': 'Error generating presigned URL for Resume', 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR.value}
            update_expression += "resumeURL = :resumeURL, "
            expression_attribute_values[':resumeURL'] = filekey
            presigned_urls['resume'] = presigned_url_resume
            update_document_entity(counselor_id, resume_key, filekey, 'RESUME', user_id)

        # Handle Experience Certificate
        if 'experience_certificateURL' in data:
            old_certificate_url = counselor.get('experience_certificateURL')
            if old_certificate_url:
                s3.delete_object(Bucket=S3_BUCKET, Key=old_certificate_url)
            filekey = data['experience_certificateURL']
            cert_key = filekey.split('/')[-1]
            presigned_url_cert = generate_presigned_url(cert_key, 'application/pdf', counselor_id, 'exp_certificate')
            if not presigned_url_cert:
                return {'success': False, 'message': 'Error generating presigned URL for Experience Certificate', 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR.value}
            update_expression += "experience_certificateURL = :experience_certificateURL, "
            expression_attribute_values[':experience_certificateURL'] = filekey
            presigned_urls['experience_certificate'] = presigned_url_cert
            update_document_entity(counselor_id, cert_key, filekey, 'EXPERIENCE_CERTIFICATES', user_id)

        # Finalize update
        if update_expression != "SET ":
            updated_at = format_datetime(datetime.now())
            update_expression += "updated_by = :updated_by, updated_at = :updated_at"
            expression_attribute_values[":updated_by"] = user_id
            expression_attribute_values[":updated_at"] = updated_at

            # Remove trailing comma from update_expression
            update_expression = update_expression.rstrip(', ')

            # Perform DynamoDB update
            counselor_table.update_item(
                Key={'counselorId': counselor_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values
            )

            response_data = {
                'success': True,
                'message': 'Counselor updated successfully',
                'presigned_urls': presigned_urls,
                'statusCode': HTTPStatus.OK.value,
                'updated_by': user_id
            }
        else:
            response_data = {
                'success': False,
                'message': 'No fields to update',
                'statusCode': HTTPStatus.BAD_REQUEST.value
            }

    except ClientError as e:
        response_data = {
            'success': False,
            'message': f'Error updating counselor: {str(e)}',
            'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR.value
        }
    except Exception as e:
        response_data = {
            'success': False,
            'message': f'Unexpected error occurred: {str(e)}',
            'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR.value
        }

    return response_data

def delete_counselor(counselor_id, data):
    try:
        counselor = counselor_table.get_item(Key={'counselorId': counselor_id}).get('Item')
        if not counselor:
            response_data = {
                'success': False,
                'message': f'Counselor with ID {counselor_id} not found.',
                'statusCode': HTTPStatus.NOT_FOUND.value
            }
            return response_data

        user_id = data.get('user_id')  

        counselor_table.update_item(
            Key={'counselorId': counselor_id},
            UpdateExpression="SET deleted_by = :deleted_by, deletedAt = :deleted_at, isActive = :isActive",
            ExpressionAttributeValues={
                ':deleted_by': user_id,
                ':deleted_at': format_datetime(datetime.now()),
                ':isActive': False
            }
        )
        document_delete_response = delete_documents(counselor_id, user_id)
        response_data = {
            'success': True,
            'message': f'Counselor with ID {counselor_id} deleted successfully.',
            'statusCode': HTTPStatus.OK.value,
            'deleted_by': user_id,
            'deleted_at': format_datetime(datetime.now()),
            'isActive': False,
            'documents_deleted': document_delete_response 
        }
        return response_data

    except ClientError as e:
        response_data = {
            'success': False,
            'message': f'Error deleting counselor: {str(e)}',
            'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR.value
        }
        return response_data
    except Exception as e:
        response_data = {
            'success': False,
            'message': f'Unexpected error occurred: {str(e)}',
            'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR.value
        }
        return response_data




