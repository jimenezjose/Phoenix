from flask_restful import Resource, reqparse
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
		parser.add_argument('name', required=True) 
		args = parser.parse_args()
		return {"message" : "args: " + str(args)}

	def add_all_resources(api, path):
		Hostname.add_all_resources(api, path + '/<string:hostname>')
