from flask_restful import Resource

def add_all_resources(api, path):
        api.add_resource(Tests, path)
        # recursively add all sub-resources
        Tests.add_all_resources(api, path)

''' /tests '''
class Tests(Resource):
	def get(self):
		return {"message": "Get all tests (id, name)"}

	def add_all_resources(api, path):
                return

