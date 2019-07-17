from api.db import get_db
from .details import Details
from .testsID import TestsID

from flask_restful import Resource

class Tests(Resource):
  """Tests resource with class design inherited from flask_restful Resource."""
  def get(self):
    """GET request for all tests (id, name)."""
    db = get_db()
    cursor = db.cursor()
    
    # query for all tests
    sql_query = """
        SELECT id, name 
        FROM tests
    """
    cursor.execute(sql_query)
    records = cursor.fetchall()

    return {'message': 'tests (id, name): {}'.format(records)}

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
