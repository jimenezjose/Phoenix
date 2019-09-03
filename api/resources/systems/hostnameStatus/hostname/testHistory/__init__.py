from api.db import (
    get_database_schema,
    get_table,
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
    parser = reqparse.RequestParser()
    validate(hostname_status=hostname_status, hostname=hostname, http_error_code=404)

    authorized_tables = ['hostnames', 'tests', 'tests_runs', 'statuses']
    filter = get_database_schema(authorized_tables)
    duplicate_fields = set()

    # find duplicate field names
    unique_field_set = set()
    for table in filter:
      for field in filter[table]:
        if field in unique_field_set:
          duplicate_fields.add(field)
        else:
          unique_field_set.add(field)

    # add query parameters 
    for table in filter:
      for field in filter[table]:
        if field in duplicate_fields:
          # clarify field by prepending unique table name
          field = '{}_{}'.format(table, field)
        parser.add_argument(field, type=str, location='args')
    args = parser.parse_args()

    # populate filter with query parameters
    for table in filter:
      for field in filter[table]:
        index = field
        if field in duplicate_fields:
          # clarify unique field index in args
          index = '{}_{}'.format(table, field)
        value = args[index]
        filter[table].update({field : value})

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
