from flask_restful import Resource
  
def add_all_resources(api, path):
        api.add_resource(Status, path)
        # recursively add all sub-resources
        Status.add_all_resources(api, path)

''' testruns/<int:id>/status '''
class Status(Resource):
	def put(self, id):
		return {"message": "PUT status_id=" + str(id)}

	def add_all_resources(api, path):
		return

