from .start import Start
from .testsrunsID import TestsrunsID
from api.db import (
    execute_sql,
    NULL_TIMESTAMP,
    get_running_tests,
    STATUS_RUNNING)

from flask_restful import Resource

class Testsruns(Resource):
  """Testruns resource with class design inherited from flask_restful Resource."""

  def get(self):
    """GET request for all current running tests across all systems"""
    
    running_tests = get_running_tests()

    return {'tests_runs' : running_tests}

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
