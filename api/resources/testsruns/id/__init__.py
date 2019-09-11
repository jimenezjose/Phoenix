from api.db import get_db, get_table, validate
# local resources
from .log import TestsrunsLog
from .status import TestsrunsStatus

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
            Status Code: 200 OK
                * table row dictionary from 'tests_runs' with row id = 'id'.
        Failure:
            Status Code: 404 Not Found
                * testsruns row 'id' does not exists in database.
    """
    validate(tests_runs_id=id, http_error_code=404)
    tests_run = get_table('tests_runs', tests_runs_id=id)
    return tests_run

  @staticmethod
  def add_all_resources(api, path):
    """Recursively adds all sub-resources in the 'api/testsruns/<int:id>' resource.

    Args:
        api:  flask_restful Api object.
        path: string path for current resource. Example: 'api/testsruns/<int:id>'
    """
    # register testruns 'TestrunsID' as an api resource
    api.add_resource(TestsrunsID, path)
    # directly add sub-resources of testruns 'TestrunsID'
    TestsrunsLog.add_all_resources(api, '{}/log'.format(path))
    TestsrunsStatus.add_all_resources(api, '{}/status'.format(path))
