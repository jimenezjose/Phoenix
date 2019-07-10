from flask_restful import Resource, reqparse
from api.db import get_db
#local resources
from .hostname import Hostname

def add_all_resources(api, path):
        api.add_resource(Systems, path)
        # recursively add all sub-resources
        Systems.add_all_resources(api, path)

''' /systems '''
class Systems(Resource):
	def get(self):
		return {"message": "GET all unretured systems"}

	def post(self):
		parser = reqparse.RequestParser()
		parser.add_argument('first_name', required=True) 
		parser.add_argument('last_name', required=True) 
		parser.add_argument('age', type=int, required=True) 
		args = parser.parse_args()
		#db = get_db()
		#cursor = db.cursor()
		#sql = "INSERT INTO develop (first_name, last_name, age) VALUES (%s, %s, %s)"
		#val = ("Virgilio", "Anaya", 17)
		#cursor.execute(sql, val)
		#db.commit()
		return {"message" : "args: " + str(args['first_name'])}

	def add_all_resources(api, path):
		Hostname.add_all_resources(api, path + '/<string:hostname>')
