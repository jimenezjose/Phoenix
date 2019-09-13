from api.db import (
    add_filter_query_parameters,
    get_table,
    parse_filter_query_parameters,
    validate,
    zip_params)

from flask_restful import (
    Resource, 
    reqparse)

class TestHistory(Resource):
  """History resource to fetch all running tests, queued tests, and test history."""

  def get(self, hostname_status, hostname):
    """GET request for all info on tests_runs associated with the hostname.

    Args:
        hostname: string name of system hostname passed through url.

    Returns:
        Table dictionary of tests_runs with applied query paramters for filtering.

        Success:
            Status Code: 200 OK
                * return tests runs information
        Failure:
            Status Code: 404 Not Found
                * Invalid url - invalid hostname_status or hostname
    """
    validate(hostname_status=hostname_status, hostname=hostname, http_error_code=404)
    parser = reqparse.RequestParser()

    add_filter_query_parameters(parser, 'tests_runs')
    args = parser.parse_args()
    filter = parse_filter_query_parameters(args, 'tests_runs')

    # overwrite filter with static info from uri
    static_params = zip_params(
        hostname=hostname, 
        hostname_status=hostname_status
    )
    filter.update(static_params)

    # query for filtered test-history
    tests_runs = get_table('tests_runs', constraints=filter)

    return {'tests_runs' : tests_runs}, 200

  @staticmethod  
  def add_all_resources(api, path):
    """Recursively adds all sub-resources in the 'test' endpoint.

    Args:
        api:  flask_restful Api object.
        path: string path for current resource. Example: 'api/systems/.../test'
    """
    # register tests as an api resource with the given path
    api.add_resource(TestHistory, path)
    # directly add sub-resources of 'test-history' <HERE>
