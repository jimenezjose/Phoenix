from .log import TestsrunsLog
from .update import TestsrunsUpdate
from api.db import (
    get_table, 
    validate)

from flask_restful import Resource

class TestsrunsID(Resource):
  """testsruns/<int:id> resource to get all info about a testsrun."""

  def get(self, tests_runs_id):
    """GET request for (hostname, tests name, start time, end time, notes, config, scratch)
    on testsrun with url passed 'id'

    Args:
        tests_runs_id : Integer identification of a specific testsrun in interest passed 
                        through url.
    Returns:
        Success:
            Status Code: 200 OK
                * table row dictionary from 'tests_runs' with row id = 'id'.
        Failure:
            Status Code: 404 Not Found
                * testsruns row 'id' does not exists in database.
    """
    validate(tests_runs_id=tests_runs_id, http_error_code=404)
    tests_run = get_table('tests_runs', tests_runs_id=tests_runs_id)
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
    TestsrunsUpdate.add_all_resources(api, '{}/update'.format(path))
