import uuid
import boto3
from flask import jsonify
from app.models.student_model import student_table
from app.models.user_model import user_table
from botocore.exceptions import ClientError

s3 = boto3.client('s3')
S3_BUCKET = 'wgc-student-bucket-2'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_presigned_url(object_name, expiration=3600):
    try:
        return s3.generate_presigned_url('put_object',
                                         Params={'Bucket': S3_BUCKET,
                                                 'Key': object_name},
                                         ExpiresIn=expiration)
    except ClientError as e:
        print(f"Error generating presigned URL: {e}")
        return None

def add_student(data):
    user_id = data.get('userId')
    student_id = str(uuid.uuid4())
    student_details = {
        'CurrentSchoolOrCollege': data.get('CurrentSchoolOrCollege'),
        'Secondary': data.get('Secondary'),
        'HigherSecondary': data.get('HigherSecondary'),
        'Specialization': data.get('Specialization'),
        'Subject': data.get('Subject'),
        'Number': data.get('Number'),
        'ParentGuardianName': data.get('ParentGuardianName'),
        'ParentGuardianEmail': data.get('ParentGuardianEmail'),
        'ParentGuardianContactNumber': data.get('ParentGuardianContactNumber'),
        'ParentGuardianProfession': data.get('ParentGuardianProfession'),
        'ContactNumber': data.get('ContactNumber'),
        'Dob': data.get('Dob'),
        'Graduate': data.get('Graduate'),
        'Gender': data.get('Gender'),
        'Address': data.get('Address'),
        'State': data.get('State'),
        'District': data.get('District'),
        'City': data.get('City'),
        'PostalCode': data.get('PostalCode'),
        'LanguagesSpoken': data.get('LanguagesSpoken'),
        'EmergencyContactName': data.get('EmergencyContactName'),
        'EmergencyContactNumber': data.get('EmergencyContactNumber')
    }

    photo_filename = data.get('photoURL')
    upload_data = None

    if photo_filename and allowed_file(photo_filename):
        object_name = f"{student_id}/{photo_filename}"
        presigned_url = generate_presigned_url(object_name)

        if presigned_url:
            student_details['PhotoURL'] = object_name
            upload_data = {
                'presignedUrl': presigned_url,
                'photoUrl': object_name
            }
        else:
            return jsonify({'error': 'Failed to generate pre-signed URL'}), 500

    try:
        response = user_table.get_item(Key={'id': user_id})
        user_details = response.get('Item')

        if not user_details:
            return jsonify({'error': 'User not found'}), 404

        user_details_mapped = {
            'Email': user_details.get('email'),
            'FirstName': user_details.get('firstname'),
            'LastName': user_details.get('lastname'),
            'ContactNumber': user_details.get('contactNo'),
            'Country': user_details.get('country'),
            'TimeZone': user_details.get('timezone'),
        }

        full_details = {**student_details, **user_details_mapped, 'studentId': student_id}
        student_table.put_item(Item=full_details)
        
        response_data = {
            'message': 'Student details added successfully',
            'studentId': student_id
        }
        if upload_data:
            response_data['uploadData'] = upload_data
        
        return jsonify(response_data), 201

    except Exception as e:
        print(f"Error adding student: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
def get_student(studentId):
    try:
        response = student_table.get_item(Key={'studentId': studentId})
        student_details = response.get('Item')
        
        if student_details:
            return jsonify({
                'success': True,
                'data': student_details,
                'message': 'Student details retrieved successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Student not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

def get_all_students():
    try:
        response = student_table.scan()
        students = response.get('Items', [])
        return jsonify({
            'success': True,
            'data': students,
            'message': 'All student details retrieved successfully',
            'count': len(students)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

def update_student(studentId, data):
    try:
        response = student_table.get_item(Key={'studentId': studentId})
        if 'Item' not in response:
            return jsonify({'error': 'Student not found'}), 404

        update_expression = "set "
        expression_attribute_values = {}
        
        old_photo_url = response['Item'].get('PhotoURL')

        for key, value in data.items():
            if key != 'photoURL' and value:
                update_expression += f"{key} = :{key}, "
                expression_attribute_values[f":{key}"] = value
        
        new_photo_filename = data.get('photoURL')
        presigned_url = None
        if new_photo_filename and allowed_file(new_photo_filename):
            new_object_name = f"{studentId}/{new_photo_filename}"
            presigned_url = generate_presigned_url(new_object_name)
            
            if presigned_url:
                update_expression += "PhotoURL = :PhotoURL, "
                expression_attribute_values[':PhotoURL'] = new_object_name
                
                # Delete old photo if exists
                if old_photo_url:
                    s3.delete_object(Bucket=S3_BUCKET, Key=old_photo_url)
            else:
                return jsonify({'error': 'Failed to generate pre-signed URL for new photo'}), 500
        
        # Remove the trailing comma and space
        update_expression = update_expression.rstrip(', ')

        # Check if there are attributes to update
        if not expression_attribute_values:
            return jsonify({'error': 'No valid fields provided for update'}), 400

        student_table.update_item(
            Key={'studentId': studentId},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values
        )

        response_data = {
            'message': 'Student updated successfully',
            'studentId': studentId
        }
        if presigned_url:
            response_data['uploadData'] = {
                'presignedUrl': presigned_url,
                'photoUrl': new_object_name
            }

        return jsonify(response_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def delete_student(studentId):
    try:
        response = student_table.get_item(Key={'studentId': studentId})
        if 'Item' not in response:
            return jsonify({'error': 'Student not found'}), 404
        
        student_data = response['Item']
        photo_url = student_data.get('PhotoURL')
        
        student_table.delete_item(Key={'studentId': studentId})
        
        if photo_url:
            s3.delete_object(Bucket=S3_BUCKET, Key=photo_url)
        
        return jsonify({'message': 'Student deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

