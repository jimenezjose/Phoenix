from flask_restful import Resource

def add_all_resources(api, path):
        api.add_resource(Log, path)
        # recursively add all sub-resources
        Log.add_all_resources(api, path)

''' /testruns/<int:id>/log '''
class Log(Resource):
	def post(self, id):
		return {"message":"Upload log to testrun id=" + str(id)}

	@staticmethod
	def add_all_resources(api, path):
		return
