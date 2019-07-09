from flask_restful import Resource

def add_all_resources(api, path):
	api.add_resource(Details, path)
	# recursively add all sub-resources
	Details.add_all_resources(api, path)

''' tests/details '''
class Details(Resource):
	def get(self):
		return {"message" : "Get all tests' info"}

	def add_all_resources(api, path):
		# recursively add sub-packaged resources
		return
