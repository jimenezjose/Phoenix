from flask_restful import Resource
# local resources
from .details import Details

def add_all_resources(api, path):
        api.add_resource(Tests, path)
        # recursively add all sub-resources
        Tests.add_all_resources(api, path)

''' /tests '''
class Tests(Resource):
	def get(self):
		return {"message": "Get all tests (id, name)"}

	@staticmethod
	def add_all_resources(api, path):
		# recursively add sub-packaged resources
		Details.add_all_resources(api, path + '/details')

