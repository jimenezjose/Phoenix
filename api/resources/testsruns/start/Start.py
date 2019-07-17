from flask_restful import Resource

''' /testruns/start '''
class Start(Resource):
  def post(self):
    return {"message": "POST hostname and test id, returns new testrun id"}

def add_all_resources(api, path):
  api.add_resource(Start, path)
