# local resources
from .start import Start
from .info import Info

from flask_restful import Resource

def add_all_resources(api, path):
  """Recursively adds all sub-resources in the 'testruns' resource.

  Args:
      api:  flask_restful Api object.
      path: string path for current resource. Example: 'api/testruns'
  """
  api.add_resource(Testruns, path)
  Testruns.add_all_resources(api, path)

class Testruns(Resource):
  """Testruns resource with class design inheritedi from flask_restful Resource."""
  def get(self):
    """GET request for TODO"""
    return {"TODO": "Get all current running tests"}

  @staticmethod
  def add_all_resources(api, path):
    """Directly adds all sub-resources of 'testruns'.

    Args:
        api:  flask_restful Api object.
        path: string path for current resource. Example: 'api/testruns'
    """
    Start.add_all_resources(api, path + '/start')
    Info.add_all_resources(api, path + '/<int:id>')

