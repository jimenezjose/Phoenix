from api.db import get_db, validate, update, get_table_fields, get_table
from flask_restful import Resource, reqparse, abort

class TestsrunsStatus(Resource):

  def put(self, id):
    """Updates testsruns status."""
    validate(tests_runs_id=id, http_error_code=404)

    # require status name parameter from request.
    parser = reqparse.RequestParser()
    parser.add_argument('statuses_name', type=str)
    parser.add_argument('config', type=str)
    parser.add_argument('notes', type=str)
    parser.add_argument('scratch', type=str)
    args = parser.parse_args()

    statuses = {}
    if args['statuses_name']:
      # get statuses full profile (id, name)
      validate(statuses_name=args['statuses_name'], http_error_code=409)
      data = get_table('statuses', statuses_name=args['statuses_name'])
      statuses = data[0]

    values = {}
    for field in get_table_fields('tests_runs'):
      # set up tests_runs fields to be updated with args
      if field in args:
        values.update({field : args[field]})
      elif field == 'statuses_id' and statuses:
        values.update({field : statuses['id']})

    updated_tests_runs = update('tests_runs', id, values)
    return updated_tests_runs
    
  @staticmethod
  def add_all_resources(api, path):
    """Recursively adds all sub-resources in the 'test' endpoint.

    Args:
        api:  flask_restful Api object.
        path: string path for current resource. Example: 'api/systems/.../test'
    """
    # register systems as an api resource
    api.add_resource(TestsrunsStatus, path)
    # directly add sub-resources of 'status' <HERE>
  
