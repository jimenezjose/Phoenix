from api.db import get_db
from api.db import NULL_TIMESTAMP

from flask_restful import Resource

class Test(Resource):
  """Test resource with class design inherited from flask_restful Resource."""

  def get(self, hostname):
    """GET request for currently running test on system hostname

    Args:
        hostname: string name of system hostname passed through url.
    """
    db = get_db()
    cursor = db.cursor()
    
    # query for currently running tests
    sql_query = """
        SELECT tests_runs.id 
        FROM tests_runs, hostnames
        WHERE hostnames.id = tests_runs.hostnames_id
        AND hostnames.hostname = %s
        AND tests_runs.end_timestamp = %s
    """
    values = (hostname, NULL_TIMESTAMP)
    cursor.execute(sql_query, values)
    records = cursor.fetchall()

    if not records:
      # no test runs currently running, return 404 Not Found error.
      return {'message' : 'No current tests running on {}.'.format(hostname)}, 404

    # otherwise list test_run id's, returning 202 OK.
    return {'message' : '{} currently running tests with tests_runs id = {}'.format(hostname, records)}, 200

def add_all_resources(api, path):
  """Recursively adds all sub-resources in the 'test' endpoint.

  Args:
      api:  flask_restful Api object.
      path: string path for current resource. Example: 'api/systems/.../test'
  """
  # register tests as an api resource
  api.add_resource(Test, path)
  # directly add sub-resources of tests <HERE>
