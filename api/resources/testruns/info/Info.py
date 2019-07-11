from flask_restful import Resource
# local resources
from .log import Log
from .status import Status

def add_all_resources(api, path):
        api.add_resource(Info, path)
        # recursively add all sub-resources
        Info.add_all_resources(api, path)

class Info(Resource):
	def get(self, id):
		return {"message": "Get info about testrun id=" + str(id)}

	@staticmethod
	def add_all_resources(api, path):
		# recursively add all sub-packaged resources
		Log.add_all_resources(api, path + '/log')
		Status.add_all_resources(api, path + '/status')
