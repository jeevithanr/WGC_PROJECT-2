def validate_user_data(data):

    required_fields = ['firstname', 'lastname', 'email', 'contactNo', 'country', 'timezone']
    
    for field in required_fields:
        if not data.get(field):
            return False, f"Missing required field: {field}"

    return True, ""

def validate_email(email):
  
    if "@" in email and "." in email:
        return True
    return False
