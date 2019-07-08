from flask_restful import Resource
# local resour

def add_all_resources(api, path):
	api.add_resource(Hostname, path)
	# recursively add all sub-resources
	Hostname.add_all_resources(api, path)

''' systems/<string:hostname> '''
class Hostname(Resource):
	def get(self, hostname):
		return {"message" : "Get info about unretired system " + hostname + " with id: " + str(int(hostname[-1:]))}

	def delete(self, hostname):
		return {"message" : "DELETE: Set " + hostname + " as retired with id: " + str(int(hostname[-1:]))}

	def add_all_resources(api, path):
		# recursively add sub-packaged resources
		return

