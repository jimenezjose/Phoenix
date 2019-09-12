from .id import TestslogsID
from api.db import (
    execute_sql, 
    get_data_by_id, 
    get_table,
    validate)
from flask_restful import (
    Resource, 
    reqparse,
    request)

class TestsrunsLog(Resource):
  """testsruns/<int:id>/log resource to upload new logs for a testsrun."""

  def get(self, tests_runs_id):
    """GET request for tests_logs_ids that contain the fileblobs associated with testsruns_id""" 
    # TODO Not implemented
    validate(tests_runs_id=tests_runs_id, http_error_code=404)
    table_name = 'tests_logs' 

    data = execute_sql("""
        SELECT id AS tests_logs_id 
        FROM `{}`
        WHERE tests_runs_id = '{}'
    """.format(table_name, tests_runs_id), dictionary=False) 

    tests_logs_list = [row[0] for row in data]

    return {'tests_logs' : tests_logs_list}, 501
    

  def post(self, tests_runs_id):
    """POST request to upload a log associated with a testsrun.

    Args: 
        id: integer representation of a unique testsrun passed thorugh url.
    """ 
    # TODO Not implemented. 
    # currently writing blob directly to db 
    # future use blob store
    validate(tests_runs_id=tests_runs_id, http_error_code=404)

    return request.files['File']

    blob = ' '.join(format(ord(x), 'b') for x in request.data)
    table_name = 'tests_logs'    

    rowid = execute_sql("""
        INSERT INTO `{}`
        (tests_runs_id, fileblob) VALUES ('{}', '{}')
    """.format(table_name, tests_runs_id, blob), db_commit=True)

    return get_data_by_id('tests_logs', rowid), 501

  @staticmethod
  def add_all_resources(api, path):
    """Recursively adds all sub-resources in the 'log' resource.

    Args:
        api:  flask_restful Api object.
        path: string path for current resource. Example: 'api/testsruns/<int:id>/log'
    """
    # registers log as an api resource
    api.add_resource(TestsrunsLog, path)
    # directly add sub-resources of log <HERE>
    TestslogsID.add_all_resources(api, '{}/<int:tests_logs_id>'.format(path))
