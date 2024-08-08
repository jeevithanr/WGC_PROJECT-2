from flask import request
from app.services.student_service import add_student, get_student, get_all_students, update_student, delete_student

def init_student_routes(app):
    @app.route('/add_student', methods=['POST'])
    def add_student_route():
        data = request.form
        files = request.files
        return add_student(data, files)
    
    @app.route('/get_student/<string:studentId>', methods=['GET'])
    def get_student_route(studentId):
        return get_student(studentId)
    
    @app.route('/get_all_students', methods=['GET'])
    def get_all_students_route():
        return get_all_students()
    
    @app.route('/update_student/<string:studentId>', methods=['PUT'])
    def update_student_route(studentId):
        data = request.get_json()
        return update_student(studentId, data)
    
    @app.route('/delete_student/<string:studentId>', methods=['DELETE'])
    def delete_student_route(studentId):
        return delete_student(studentId)
