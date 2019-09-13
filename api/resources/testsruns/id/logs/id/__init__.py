from api.db import get_data_by_id, validate
from flask import send_from_directory
from flask_restful import (
    abort,
    Resource,
    reqparse)

class TestslogsID(Resource):

  def get(self, tests_runs_id, tests_logs_id):
    """Gets binary data of tests log"""
    validate(tests_runs_id=tests_runs_id, tests_logs_id=tests_logs_id)
    tests_log = get_data_by_id('tests_logs', tests_logs_id)

    if tests_runs_id != tests_log['tests_runs_id']:
      # invalid url - no log with under given tests_runs id
      error_msg = 'tests_runs_id=\'{}\' with tests_logs_id=\'{}\' Not Found.'
      abort(404, message=error_msg.format(tests_runs_id, tests_logs_id))

    # absolute path to file log
    filepath = tests_log['location']
    # unique name of file for log in disk
    uuid_filename = filepath.split('/')[-1]
    # path to folder that hold the log file in disk
    upload_folder = filepath.replace(uuid_filename, '')

    # user friendly name of test log
    friendly_filename = tests_log['files_name']
    
    file_attachment = send_from_directory(
        upload_folder, 
        uuid_filename,
        as_attachment=True,
        attachment_filename=friendly_filename
    )

    return file_attachment

  @staticmethod
  def add_all_resources(api, path):
    """Recursively adds all sub-resources. 

    Args:
        api:  flask_restful Api object.
        path: string path for current resource. Example: 'api/testsruns/<int:id>'
    """
    # register current path as a resource
    api.add_resource(TestslogsID, path)
    # directly add sub-resources <HERE>
    
