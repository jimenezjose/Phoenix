# KEY 'file' type file 
# VALUE <file> 
# CONTENT TYPE application/octet-stream or multipart/form-data
# flask documentation recommends mulipart/form-data: 
# source: http://flask.palletsprojects.com/en/1.0.x/patterns/fileuploads/

from .id import TestslogsID
from api.db import (
    delete_tests_log,
    get_data_by_id, 
    get_table,
    insert_tests_log,
    validate)
from flask_restful import (
    abort,
    Resource, 
    reqparse,
    request)

class TestsrunsLogs(Resource):
  """Upload/Delete log files to testsruns. Also get log file ids."""

  def get(self, tests_runs_id):
    """GET request for tests_logs_ids that contain the fileblobs associated with testsruns_id""" 
    validate(tests_runs_id=tests_runs_id, http_error_code=404)
    tests_logs = get_table('tests_logs', tests_runs_id=tests_runs_id, raw=True)
    return {'tests_logs' : tests_logs}, 200
    
  def post(self, tests_runs_id):
    """POST request to upload a log associated with a testsrun.

    Args: 
        tests_runs_id: integer representation of a unique testsrun passed thorugh url.
    """ 
    validate(tests_runs_id=tests_runs_id, http_error_code=404)

    inserted_tests_logs = []
    for a_file in request.files.getlist('file'):
      if a_file.filename:
        # insert file log to database and disk
        tests_logs_id = insert_tests_log(tests_runs_id, a_file)
        data = get_data_by_id('tests_logs', tests_logs_id, raw=True)
        inserted_tests_logs.append(data)        
    return {'tests_logs' : inserted_tests_logs}, 201

  def delete(self, tests_runs_id):
    """Delete tests_log file from disk and db."""
    validate(tests_runs_id=tests_runs_id, http_error_code=404)
    # require tests_logs_id paramter in POST body 
    parser = reqparse.RequestParser()
    parser.add_argument('tests_logs_id', type=int, required=True)
    args = parser.parse_args()
    # validate tests logs id exists
    validate(tests_logs_id=args['tests_logs_id'], http_error_code=404)

    tests_log = get_data_by_id('tests_logs', args['tests_logs_id'])
    if tests_runs_id != tests_log['tests_runs_id']:
      # log id does not belong to tests_run - conflict
      error_msg = 'tests_runs_id=\'{}\' with tests_logs_id=\'{}\' Not Found.'
      abort(409, message=error_msg.format(tests_runs_id, args['tests_logs_id']))

    # delete log from disk and db
    deleted_log = delete_tests_log(args['tests_logs_id'])
    return deleted_log
    
  @staticmethod
  def add_all_resources(api, path):
    """Recursively adds all sub-resources in the 'log' resource.

    Args:
        api:  flask_restful Api object.
        path: string path for current resource. Example: 'api/testsruns/<int:id>/log'
    """
    # registers log as an api resource
    api.add_resource(TestsrunsLogs, path)
    # directly add sub-resources of log <HERE>
    TestslogsID.add_all_resources(api, '{}/<int:tests_logs_id>'.format(path))
