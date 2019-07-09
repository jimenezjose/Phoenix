from flask_restful import Resource

def add_all_resources(api, path):
        api.add_resource(Start, path)
        # recursively add all sub-resources
        Start.add_all_resources(api, path)

''' /testruns/start '''
class Start(Resource):
	def post(self):
		return {"message": "POST hostname=sfo2-aag-12-sr1, returns new testrun id"}

	def add_all_resources(api, path):
		return

