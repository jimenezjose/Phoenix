from api.db import (
    validate,
    get_tests_runs_table)

from flask_restful import Resource

class TestsrunsStatus(Resource):

  def get(self, hostname_status, hostname, tests_runs_status):
    """GET all history of given hostname"""
    validate(hostname_status=hostname_status, hostname=hostname, 
             tests_runs_status=tests_runs_status)

    tests_runs = get_tests_runs_table(hostname, tests_runs_status=tests_runs_status)

    return {'tests_runs' : tests_runs}

  @staticmethod
  def add_all_resources(api, path):
    """Recursively adds all sub-resources in the 'testsrunsStatus' endpoint.

    Args:
        api:  flask_restful Api object.
        path: string path for current resource. Example: 'api/systems/.../test/running'
    """
    # register tests as an api resource
    api.add_resource(TestsrunsStatus, path)
    # directly add sub-resources of tests <HERE>
