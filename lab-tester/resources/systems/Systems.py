from flask_restful import Resource
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
		return {"message": "POST hostname=sfo2-aag-12-sr1, adds new unretired system=sfo2-aag-12-sr1"}

	def add_all_resources(api, path):
		Hostname.add_all_resources(api, path + '/<string:hostname>')
