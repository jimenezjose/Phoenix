from .start import Start
from .id import TestsrunsID
from api.db import (
    add_filter_query_parameters,
    parse_filter_query_parameters,
    get_running_tests)

from flask_restful import (
    Resource, 
    reqparse)

class Testsruns(Resource):
  """Testruns resource with class design inherited from flask_restful Resource."""

  def get(self):
    """GET request for all current running tests across all systems"""
    parser = reqparse.RequestParser()

    add_filter_query_parameters(parser, 'tests_runs')
    args = parser.parse_args()
    filter = parse_filter_query_parameters(args, 'tests_runs')

    running_tests = get_running_tests(constraints=filter)

    return {'tests_runs' : running_tests}, 200

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
