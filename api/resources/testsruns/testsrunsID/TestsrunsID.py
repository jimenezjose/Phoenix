# local resources
from .log import Log
from .status import Status

from flask_restful import Resource

class TestsrunsID(Resource):
  def get(self, id):
    return {"message": "Get info about testrun id=" + str(id)}

def add_all_resources(api, path):
  """Recursively adds all sub-resources in the 'api/testsruns/<int:id>' resource.

  Args:
      api:  flask_restful Api object.
      path: string path for current resource. Example: 'api/testsruns/<int:id>'
  """
  # register testruns 'TestrunsID' as an api resource
  api.add_resource(TestsrunsID, path)
  # directly add sub-resources of testruns 'TestrunsID'
  Log.add_all_resources(api, '{}/log'.format(path))
  Status.add_all_resources(api, '{}/status'.format(path))
