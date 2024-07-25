import uuid
from app.models.student_model import student_table
from app.models.user_model import user_table
from flask import jsonify

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
        'EmergencyContactNumber': data.get('EmergencyContactNumber'),
        'PhotoURL': data.get('PhotoURL')
    }
    
    try:
        # Retrieve basic details from the User Table
        response = user_table.get_item(Key={'id': user_id})
        user_details = response.get('Item')

        if user_details:
            user_details_mapped = {
                'Email': user_details.get('email'),
                'FirstName': user_details.get('firstname'),
                'LastName': user_details.get('lastname'),
                'ContactNumber': user_details.get('contactNo'),
                'Country': user_details.get('country'),
                'TimeZone': user_details.get('timezone'),
            }

            # Merge basic details with student-specific details
            full_details = {**student_details, **user_details_mapped}
            full_details['studentId'] = student_id

            # Put the merged details into the Student Table
            student_table.put_item(Item=full_details)
            return jsonify({'message': 'Student details added successfully', 'studentId': student_id}), 201
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
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
        for key, value in data.items():
            update_expression += f"{key} = :{key}, "
            expression_attribute_values[f":{key}"] = value

        update_expression = update_expression[:-2] 
        
        student_table.update_item(
            Key={'studentId': studentId},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values
        )
        return jsonify({'message': 'Student updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def delete_student(studentId):
    try:
        response = student_table.get_item(Key={'studentId': studentId})
        if 'Item' not in response:
            return jsonify({'error': 'Student not found'}), 404

        student_table.delete_item(Key={'studentId': studentId})
        return jsonify({'message': 'Student deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
