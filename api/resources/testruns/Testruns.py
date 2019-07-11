# local resources
from .start import Start
from .info import Info

from flask_restful import Resource

def add_all_resources(api, path):
  api.add_resource(Testruns, path)
  # recursively add all sub-resources
  Testruns.add_all_resources(api, path)

''' /testruns '''
class Testruns(Resource):
  def get(self):
    return {"TODO": "Get all current running tests"}

  @staticmethod
  def add_all_resources(api, path):
    # recursively add sub-packaged resources
    Start.add_all_resources(api, path + '/start')
    Info.add_all_resources(api, path + '/<int:id>')

