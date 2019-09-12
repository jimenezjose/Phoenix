from api.db import get_data_by_id
from flask_restful import (
    Resource,
    reqparse)

class TestslogsID(Resource):

  def get(self, tests_runs_id, tests_logs_id):
    """Gets binary data of tests log"""
    data = get_data_by_id('tests_logs', tests_logs_id, raw=True)
    return data['fileblob']

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
    
