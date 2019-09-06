from .details import Details
from .testsID import TestsID
from api.db import get_table
from flask_restful import Resource

class Tests(Resource):
  """Tests resource with class design inherited from flask_restful Resource."""
  def get(self):
    """GET request for all tests (id, name)."""
    tests_table = get_table('tests')
    return {'tests' : tests_table}

  @staticmethod
  def add_all_resources(api, path):
    """Recursively adds all sub-resources in the 'test' endpoint.

    Args:
        api:  flask_restful Api object.
        path: string path for current resource. Example: 'api/tests'
    """
    # register tests as an api resource
    api.add_resource(Tests, path)
    # directly add sub-resources of tests
    Details.add_all_resources(api, '{}/details'.format(path))
    TestsID.add_all_resources(api, '{}/<int:id>'.format(path))
