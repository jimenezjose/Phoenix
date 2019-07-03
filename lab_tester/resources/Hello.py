from flask_restful import Resource

class Hello(Resource):
	def get(self):
		return {"message": "GET: Hello World!"}

	def post(self):
		return {"message": "POST: Hello World!"}
