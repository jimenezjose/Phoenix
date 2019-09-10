from api.db import (
    add_filter_query_parameters,
    parse_filter_query_parameters,
    get_table)

from flask_restful import (
    Resource,
    reqparse)

class Details(Resource):
  """Resource: 'details' to get information about all tests.""" 

  def get(self):
    """GET request for all tests' info."""
    parser = reqparse.RequestParser()

    add_filter_query_parameters(parser, 'tests_runs')
    args = parser.parse_args()
    filter = parse_filter_query_parameters(args, 'tests_runs')

    tests_commands_table = get_table('tests_commands', constraints=filter)
    return {'tests_commands' : tests_commands_table}

  @staticmethod
  def add_all_resources(api, path):
    """Recursively adds all sub-resources in the 'tests/details' resource.

    Args:
        api:  flask_restful Api object.
        path: string path for current resource. Example: 'api/tests/details'
    """
    # register 'tests/details' as an api resource
    api.add_resource(Details, path)
    # directly add sub-resources of 'details' <HERE>
