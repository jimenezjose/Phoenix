from api.db import get_db
# local resources
from .log import Log
from .status import Status

from flask_restful import Resource

class TestsrunsID(Resource):
  """testsruns/<int:id> resource to get all info about a testsrun."""

  def get(self, id):
    """GET request for (hostname, tests name, start time, end time, notes, config, scratch)
    on testsrun with url passed 'id'

    Args:
        id: integer identification of a specific testsrun in interest passed through url.  

    Returns:
        Success:
            * (All information from tests_runs with 'id')
                Status Code: 200 OK
        Failure:
            * (tests_runs 'id' not found in database)
                Status Code: 404 Not Found
    """
    db = get_db()
    cursor = db.cursor()

    # query for testsruns information
    sql_query = """
        SELECT hostnames.hostname, tests.name, tests_runs.start_timestamp, 
        tests_runs.end_timestamp, statuses.name, tests_runs.notes, tests_runs.config, 
        tests_runs.scratch
        FROM hostnames, tests, tests_runs, statuses 
        WHERE tests_runs.id = %s AND hostnames.id = tests_runs.hostnames_id 
        AND tests.id = tests_runs.tests_id AND statuses.id = tests_runs.status
    """
    values = (id,)
    cursor.execute(sql_query, values)
    records = cursor.fetchall()

    if not records:
      # resource for given id not in database, return 404 not found error
      return {'message' : 'tests_runs id: {}, Not Found.'.format(id)}, 404

    return {'message': 'testsruns_info on id = {} : (hostname, tests name, start time, end time, notes, config, scratch): {}'.format(id, records)}, 200

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
