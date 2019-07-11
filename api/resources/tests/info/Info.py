from flask_restful import Resource

def add_all_resources(api, path):
	api.add_resource(Info, path)
	# recursively add all sub-resources
	Info.add_all_resources(api, path)

''' tests/<int:id> '''
class Info(Resource):
	def get(self, id):
		return {"message" : "Get test info about test id=" + str(id)}

	@staticmethod
	def add_all_resources(api, path):
		# recursively add all sub-resources after id
		return
