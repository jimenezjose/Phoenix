from api.db import (
    get_linked_tables,
    get_database_schema,
    get_duplicate_field_names,
    get_table)

from flask_restful import (
    Resource,
    reqparse)

# TODO reduce weight of filtering with query parameters by modularizing function

class Details(Resource):
  """Resource: 'details' to get information about all tests.""" 

  def get(self):
    """GET request for all tests' info."""
    parser = reqparse.RequestParser()

    authorized_tables = get_linked_tables('tests_runs')
    filter = get_database_schema(authorized_tables)
    duplicate_fields = get_duplicate_field_names(authorized_tables)

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
