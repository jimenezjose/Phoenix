from .start import Start
from .testsrunsID import TestsrunsID
from api.db import (
    execute_sql,
    NULL_TIMESTAMP,
    STATUS_RUNNING)

from flask_restful import Resource

class Testsruns(Resource):
  """Testruns resource with class design inherited from flask_restful Resource."""

  def get(self):
    """GET request for all current running tests"""
    
    # query for all tests runs (hostname, test name, start time, test run status)
    records = execute_sql("""
        SELECT hostnames.hostname, tests.name, tests_runs.start_timestamp, tests_runs.status
        FROM hostnames, tests, tests_runs
        WHERE tests_runs.end_timestamp = '{}'
        AND tests_runs.status = '{}'
        AND tests_runs.hostnames_id = hostnames.id
        AND tests_runs.tests_id = tests.id
    """.format(NULL_TIMESTAMP, STATUS_RUNNING))

    return {'message': 'running tests (hostname, test name, start time, test run status): {}'.format(records)}

  @staticmethod
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
