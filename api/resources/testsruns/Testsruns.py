from api.db import get_db, NULL_TIMESTAMP, STATUS_RUNNING
from .start import Start
from .testsrunsID import TestsrunsID

from flask_restful import Resource

class Testsruns(Resource):
  """Testruns resource with class design inherited from flask_restful Resource."""

  def get(self):
    """GET request for all current running tests"""
    db = get_db()
    cursor = db.cursor()
    
    # query for all tests runs (hostname, test name, start time, test run status)
    sql_query = """
        SELECT hostnames.hostname, tests.name, tests_runs.start_timestamp, tests_runs.status
        FROM hostnames, tests, tests_runs
        WHERE tests_runs.end_timestamp = %s 
        AND tests_runs.status = %s
        AND tests_runs.hostnames_id = hostnames.id
        AND tests_runs.tests_id = tests.id
    """
    values = (NULL_TIMESTAMP, STATUS_RUNNING)
    cursor.execute(sql_query, values)
    records = cursor.fetchall()

    return {'message': 'running tests (hostname, test name, start time, test run status): {}'.format(records)}

def add_all_resources(api, path):
  """Recursively adds all sub-resources in the 'testruns' resource.

  Args:
      api:  flask_restful Api object.
      path: string path for current resource. Example: 'api/testruns'
  """
  # register testruns as an api resource
  api.add_resource(Testsruns, path)
  # directly add sub-resources of testruns
  Start.add_all_resources(api, '{}/start'.format(path))
  TestsrunsID.add_all_resources(api, '{}/<int:id>'.format(path))
