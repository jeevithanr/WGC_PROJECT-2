import uuid
import boto3
from flask import jsonify
from botocore.exceptions import ClientError
from email.utils  import format_datetime
from app.models.counselor_model import counselor_table  # Assuming this is a DynamoDB table
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from http import HTTPStatus

# Initialize boto3 client for S3 and DynamoDB
s3 = boto3.client('s3')
S3_BUCKET = 'wgc-student-bucket-4'  # Your S3 bucket for storing counselor data if needed

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
availability_table = dynamodb.Table('CounselorAvailability')  # Assuming availability table exists


def generate_presigned_url(filename, content_type):
    try:
        counselor_id = str(uuid.uuid4())
        file_key = f"{counselor_id}/{filename}"
        if filename.lower().endswith('.png'):
            content_type = 'image/png'
        elif filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg'):
            content_type = 'image/jpeg'
        elif filename.lower().endswith('.pdf'):
            content_type = 'application/pdf'
        else:
            content_type = content_type  # Fallback to the provided content type if none of the above
           
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

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'.jpeg', '.png', '.jpg', '.pdf'}
    ext = filename.lower().rsplit('.', 1)[-1]
    is_allowed = f".{ext}" in ALLOWED_EXTENSIONS
    
    response_data = {
        'success': is_allowed,
        'message': 'File extension is allowed' if is_allowed else 'File extension is not allowed',
        'statusCode': HTTPStatus.OK.value if is_allowed else HTTPStatus.BAD_REQUEST.value
    }
    return response_data

def create_counselor(data, current_user):
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
    price = data['price']
    specialization = data['specialization']
    qualification = data['qualification']
    language_spoken = data['language_spoken']
    achievements = data['achievements']
    date_of_joining = data['date_of_joining']
    rating = Decimal(data['rating']) if 'rating' in data else Decimal('0')
    isActive = data['isActive'] if 'isActive' in data else True
    linkedinURL = data['linkedinURL'] if 'linkedinURL' in data else ''
    availability_status = data['availability_status']
    photo_name = data['PhotoURL'] if 'PhotoURL' in data else ''  
    created_at = format_datetime(datetime.now())
    updated_at = created_at

    required_fields = [
        firstName, lastName, gender, mailid, contact_number, alternate_contact_number,
        experience, date_of_birth, address, country, state, district, city, pincode,
        price, specialization, qualification, language_spoken, achievements,
        date_of_joining, availability_status
    ]
    
    if any(field is None or field == '' for field in required_fields):
        response_data= {
        'success': False,
        'message': 'All fields are required.',
        'statusCode': HTTPStatus.BAD_REQUEST.value
    }
        return response_data
    presigned_url, file_key = generate_presigned_url(photo_name,'image/jpeg')  
    if not presigned_url:
        response_data = {
        'success': False,
        'message': 'Error generating presigned URL.',
        'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR.value
        }
        return response_data

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
        'PhotoURL': file_key,  
        'created_by': current_user,
        'created_at': created_at,
        'updated_by': current_user,
        'updated_at': updated_at,
        'deletedAt': None,
        'deletedBy': None
    }

    try:
        counselor_table.put_item(Item=counselor_details)
        print(f"Presigned URL: {presigned_url}")

        response_data= {
            'success': True,
            'message': 'Counselor created successfully.',
            'totalresult': {
                'counselorId': counselor_id,
                'counselor': counselor_details,
                'presigned_url': presigned_url
            },
            'statusCode': HTTPStatus.CREATED.value
        }
        return response_data
    except ClientError as e:
        response_data = {
            'success': False,
            'message': f'Error creating counselor: {str(e)}',
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
    
def update_counselor(counselor_id, data, current_user):
    try:
        response = counselor_table.get_item(Key={'counselorId': counselor_id})
        if 'Item' not in response:
            response_data = {
                'success': False,
                'message': 'Counselor not found',
                'statusCode': HTTPStatus.NOT_FOUND.value
            }
            return response_data
        
        counselor = response['Item']
        update_expression = "SET "
        expression_attribute_values = {}
        presigned_url = None

        updatable_fields = [
            'firstName', 'lastName', 'gender', 'mailid', 'contact_number', 'alternate_contact_number',
            'experience', 'date_of_birth', 'address', 'country', 'state', 'district', 'city', 'pincode',
            'price', 'specialization', 'qualification', 'language_spoken', 'achievements',
            'date_of_joining', 'availability_status'
        ]
        
        for field in updatable_fields:
            if field in data and data[field] != counselor.get(field):
                update_expression += f"{field} = :{field}, "
                expression_attribute_values[f":{field}"] = data[field]

        if 'price' in data:
            try:
                price_value = Decimal(data['price']).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                if price_value != counselor.get('price'):
                    update_expression += "price = :price, "
                    expression_attribute_values[":price"] = price_value
            except InvalidOperation:
                response_data = {
                    'success': False,
                    'message': 'Invalid price value',
                    'statusCode': HTTPStatus.BAD_REQUEST.value
                }
                return response_data

        if 'rating' in data:
            try:
                rating_value = Decimal(data['rating']).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                if rating_value != counselor.get('rating'):
                    update_expression += "rating = :rating, "
                    expression_attribute_values[":rating"] = rating_value
            except InvalidOperation as e:
                response_data = {
                    'success': False,
                    'message': 'Invalid rating value',
                    'statusCode': HTTPStatus.BAD_REQUEST.value
                }
                return response_data

        if 'PhotoURL' in data and allowed_file(data['PhotoURL']):
            old_photo_url = counselor.get('PhotoURL')
            if old_photo_url:
                s3.delete_object(Bucket=S3_BUCKET, Key=old_photo_url)
            new_photo_filename = data['PhotoURL']
            presigned_url, new_file_key = generate_presigned_url(new_photo_filename, 'image/jpeg')
            
            if presigned_url is None or new_file_key is None:
                response_data = {
                    'success': False,
                    'message': 'Error generating presigned URL',
                    'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR.value
                }
                return response_data
            
            update_expression += "PhotoURL = :PhotoURL, "
            expression_attribute_values[':PhotoURL'] = new_file_key

            print(f"Generated presigned URL: {presigned_url}")

        if not update_expression.endswith("SET "): 
            updated_at = format_datetime(datetime.now())
            
            update_expression += "updated_by = :updated_by, updated_at = :updated_at"
            expression_attribute_values[":updated_by"] = current_user
            expression_attribute_values[":updated_at"] = updated_at

            update_expression = update_expression.rstrip(', ')

            counselor_table.update_item(
                Key={'counselorId': counselor_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values
            )

            response_data = {
                'success': True,
                'message': 'Counselor updated successfully',
                'presigned_url': presigned_url,
                'statusCode': HTTPStatus.OK.value,
                'updated_by': current_user
            }
            return response_data
        else:
            response_data = {
                'success': False,
                'message': 'No fields to update',
                'statusCode': HTTPStatus.BAD_REQUEST.value
            }
            return response_data

    except ClientError as e:
        response_data = {
            'success': False,
            'message': f'Error updating counselor: {str(e)}',
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
        
def delete_counselor(counselor_id, current_user):
    try:
        counselor = counselor_table.get_item(Key={'counselorId': counselor_id}).get('Item')
        if not counselor:
            response_data = {
                'success': False,
                'message': f'Counselor with ID {counselor_id} not found.',
                'statusCode': HTTPStatus.NOT_FOUND.value
            }
            return response_data
        photo_url = counselor.get('PhotoURL')
        counselor_table.update_item(
            Key={'counselorId': counselor_id},
            UpdateExpression="SET deleted_by = :deleted_by, deletedAt = :deleted_at, isActive = :isActive",
            ExpressionAttributeValues={
                ':deleted_by': current_user,
                ':deleted_at': format_datetime(datetime.now()),
                ':isActive': False
            }
        )
        if photo_url:
            photo_key = photo_url.split(f"https://{S3_BUCKET}.s3.amazonaws.com/")[-1]
            s3.delete_object(Bucket=S3_BUCKET, Key=photo_key)
        response_data = {
            'success': True,
            'message': f'Counselor with ID {counselor_id} deleted successfully.',
            'statusCode': HTTPStatus.OK.value,
            'deleted_by': current_user,
            'deleted_at': format_datetime(datetime.now()),
            'isActive': False
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
            'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR.value,
            'deleted_by': current_user,
            'deleted_at': None,
            'isActive': False
        }
        return response_data
    


def delete_counselor(counselor_id, current_user):
    """ Delete a counselor by ID from DynamoDB """
    try:
        counselor_table.delete_item(Key={'counselor_id': counselor_id})
        return jsonify({"message": "Counselor deleted successfully"}), HTTPStatus.OK
    except ClientError as e:
        return jsonify({"error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR


# ------------------- New Availability and S3 Logic ------------------- #

def update_availability(counselor_id, availability, current_user):
    """ Update the availability of a counselor in DynamoDB """
    try:
        # Store availability times in DynamoDB
        availability_table.put_item(Item={
            'counselor_id': counselor_id,
            'availability_id': str(uuid.uuid4()),
            'availability_times': availability,
            'updated_by': current_user,
            'updated_at': format_datetime(datetime.now())
        })
        return jsonify({"message": "Availability updated successfully"}), HTTPStatus.OK
    except ClientError as e:
        return jsonify({"error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR


def get_available_times(counselor_id):
    """ Retrieve available times for a counselor from DynamoDB """
    try:
        response = availability_table.query(
            KeyConditionExpression="counselor_id = :cid",
            ExpressionAttributeValues={':cid': counselor_id}
        )
        availability = response.get('Items', [])
        if availability:
            return jsonify(availability), HTTPStatus.OK
        else:
            return jsonify({"message": "No availability found for this counselor"}), HTTPStatus.NOT_FOUND
    except ClientError as e:
        return jsonify({"error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR


def upload_to_s3(file_data, filename):
    """ Upload a file to S3 bucket """
    try:
        s3.put_object(Bucket=S3_BUCKET, Key=filename, Body=file_data)
        return jsonify({"message": "File uploaded successfully"}), HTTPStatus.OK
    except ClientError as e:
        return jsonify({"error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
