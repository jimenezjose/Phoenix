from flask_restful import Resource

def add_all_resources(api, path):
	api.add_resource(Test, path)
	#recursively add all sub-resources
	Test.add_all_resources(api, path)

class Test(Resource):
	def get(self, hostname):
		return {"message" : "Get most recent testrun id of " + hostname}

	def add_all_resources(api, path):
		return

