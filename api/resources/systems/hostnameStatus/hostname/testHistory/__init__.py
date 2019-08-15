from .testsrunsStatus import TestsrunsStatus
from api.db import (
    execute_sql,
    get_tests_runs_table,
    get_tests_runs_queue,
    get_table_fields,
    validate)

from flask_restful import Resource, reqparse

class TestHistory(Resource):
  """History resource to fetch all running tests, queued tests, and test history."""

  def get(self, hostname_status, hostname):
    """GET request for all info on tests_runs associated with the hostname.

    Args:
        hostname: string name of system hostname passed through url.

    Returns:
        Success:
            * (tests_runs information on hostname found)
                Status Code 200 OK
        Failure:
            * (invlaid hostname/statusflag provided)
                Status Code 404 Not Found
    """
    validate(hostname_status=hostname_status, hostname=hostname)

    parser = reqparse.RequestParser()
    tests_runs_table_fields = get_table_fields('tests_runs')
    for field in tests_runs_table_fields:
      parser.add_argument(field, type=str)
    args = parser.parse_args()

    # query for currently running tests
    #tests_runs = get_tests_runs_table(hostname, filter=args)
    tests_runs = get_tests_runs_table(hostname)

    tests_records = {'tests_runs' : tests_runs}

    return tests_records

  @staticmethod  
  def add_all_resources(api, path):
    """Recursively adds all sub-resources in the 'test' endpoint.

    Args:
        api:  flask_restful Api object.
        path: string path for current resource. Example: 'api/systems/.../test'
    """
    # register tests as an api resource with the given path
    api.add_resource(TestHistory, path)
    # add a new end-point for querying specific statused tests_runs
    TestsrunsStatus.add_all_resources(api, '{}/<string:tests_runs_status>'.format(path))
