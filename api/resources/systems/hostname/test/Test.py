from flask_restful import Resource

def add_all_resources(api, path):
  """Recursively adds all sub-resources in the 'test' endpoint.

  Args:
      api:  flask_restful Api object.
      path: string path for current resource. Example: 'api/systems'
  """
  api.add_resource(Test, path)
  Test.add_all_resources(api, path)

''' systems/<string:hostname>/test '''
class Test(Resource):
  def get(self, hostname):
    return {"TODO" : "Get most recent testrun id of " + hostname}

  @staticmethod
  def add_all_resources(api, path):
    return

