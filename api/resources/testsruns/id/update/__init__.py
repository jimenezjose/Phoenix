from api.db import (
    get_table,
    get_table_fields, 
    update, 
    validate)

from flask_restful import (
    abort,
    Resource, 
    reqparse)

class TestsrunsUpdate(Resource):
  """Update testsrun paramaters such as status, config, and notes."""

  def put(self, tests_runs_id):
    """Updates testsruns table row data.
    
    Returns:
        Dictionary of updated tests_runs row.

        Success:
            Status Code: 200 OK
                * tests_runs row is updated.
        Failure:
            Status Code: 404 Not Found
                * invalid url - tests_runs_id not found.
                * 
    """
    validate(tests_runs_id=tests_runs_id, http_error_code=404)

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
      if field in args and args[field]:
        values.update({field : args[field]})
      elif field == 'statuses_id' and statuses:
        values.update({field : statuses['id']})

    if not values:
      # no data to updated
      abort(400, message='At least one parameter is required: {}'.format(args.keys()))

    updated_tests_runs = update('tests_runs', tests_runs_id, values)
    return updated_tests_runs, 200
    
  @staticmethod
  def add_all_resources(api, path):
    """Recursively adds all sub-resources in the 'test' endpoint.

    Args:
        api:  flask_restful Api object.
        path: string path for current resource. Example: 'api/systems/.../test'
    """
    # register systems as an api resource
    api.add_resource(TestsrunsUpdate, path)
    # directly add sub-resources of 'status' <HERE>
  
