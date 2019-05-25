from flask import Flask, jsonify, request, g
from flask_restful import Api, Resource
from pprint import pprint
from datetime import datetime, timedelta
from marshmallow import Schema, fields

from google.appengine.ext import ndb

app = Flask(__name__)
api = Api(app)

class StudentInfo(ndb.Model):
    """A naive Contact model."""
    # Basic info.
    name = ndb.TextProperty()
    date_of_birth = ndb.DateProperty()

    # Address info.
    address = ndb.TextProperty()

    # Phone info.
    phone_number = ndb.StringProperty()

    # Other info.
    email = ndb.StringProperty()
    # set value on create only
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    # update value every time the entity is updated
    updated_at = ndb.DateTimeProperty(auto_now=True)

class StudentInfoSerializer(Schema):
    # return url-encoded version of id
    id = fields.Function(lambda obj: obj.key.urlsafe())
    class Meta:
        fields = (
            "id", "name", "date_of_birth", "address",
            "phone_number", "email", "created_at", "updated_at"
        )

student_schema = StudentInfoSerializer()
students_schema = StudentInfoSerializer(many=True)

class Student(Resource):

    def get(self, id):
        try:
            key = ndb.Key(urlsafe=id)
            student = key.get()

            if student == None:
                response =  jsonify({"success": False, "message": "No student found with the id."})
                response.status_code = 404
                return response
            else:
                response =  jsonify({"success": True, "message": "Student fetched successfully", "data": student_schema.dump(student).data})
                response.status_code = 200
                return response

        except Exception as ex:
            # error pretty print

            response = jsonify({
                'success': False,
                'message': 'Something went wrong on when fetching form database',
                'error': str(ex)
            })
            response.status_code=500

            return response

    def delete(self, id):
        try:
            key = ndb.Key(urlsafe=id)
            key.delete()

            response =  jsonify({"success": True, "message": "Student deleted successfully"})
            response.status_code = 200
            return response

        except Exception as ex:
            response = jsonify({
                'success': False,
                'message': 'Something went wrong',
                'error': str(ex)
            })
            response.status_code=500
            return response


    def put(self, id):
        try:
            key = ndb.Key(urlsafe=id)
            student = key.get()

            if student == None:
                response =  jsonify({"success": False, "message": "No student found with the id."})
                response.status_code = 404
                return response
            else:
                body = request.json

                if 'name' in body:
                    student.name = body['name']
                if 'date_of_birth' in body:
                    student.date_of_birth  = body['date_of_birth']
                if 'address' in body:
                    student.address = body['address']
                if 'phone_number' in body:
                    student.phone_number = body['phone_number']
                if 'email' in body:
                    student.email = body['email']

                student.put()

                response =  jsonify({"success": True, "message": "Student fetched successfully", "data": student_schema.dump(student).data})
                response.status_code = 200
                return response

        except Exception as ex:
            # error pretty print

            response = jsonify({
                'success': False,
                'message': 'Something went wrong on when fetching form database',
                'error': str(ex)
            })
            response.status_code=500

            return response

class StudentList(Resource):

    def get(self):
        try:
            students = StudentInfo.query().fetch()
            response = jsonify({"success": True, "message": "Students fetched successfully", "data": students_schema.dump(students).data})
            response.status_code = 200 # or 400 or whatever
            return response

        except Exception as ex:
            # error pretty print

            response = jsonify({
                'success': False,
                'message': 'Something went wrong on creating posts',
                'error': str(ex)
            })
            response.status_code = 500

            return response

    def post(self):
        try:
            student = StudentInfo(
                name=request.json['name'],
                date_of_birth=datetime.strptime(request.json['date_of_birth'], '%Y-%m-%d'),
                address=request.json['address'],
                phone_number=request.json['phone_number'],
                email=request.json['email'])

            # write to datastore
            student.put()

            response = jsonify({'success': True, 'message': 'Student Added Successfully', 'data':student_schema.dump(student).data})
            response.status_code = 201

            return response

        except Exception as ex:
            response = jsonify({'success': False, 'message': 'Something went wrong', 'error':str(ex)})
            response.status_code = 500

            return response


api.add_resource(StudentList, '/api/students')
api.add_resource(Student, '/api/students/<id>')


if __name__ == '__main__':
    app.run(debug=True)


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def page_not_found(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500
