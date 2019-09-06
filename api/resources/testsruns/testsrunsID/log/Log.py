from api.db import get_db

from flask_restful import Resource, reqparse

''' /testruns/<int:id>/log '''
class Log(Resource):
  """testsruns/<int:id>/log resource to upload new logs for a testsrun."""

  def post(self, id):
    """POST request to upload a log associated with a testsrun.

    Args: 
        id: integer representation of a unique testsrun passed thorugh url.
    """ 
    db = get_db()
    cursor = db.cursor()
    parser = reqparse.RequestParser()

    # require ''
    #parser.add_argument('', required=True)

    return {"message":"Upload log to testrun id=" + str(id)}

def add_all_resources(api, path):
  """Recursively adds all sub-resources in the 'log' resource.

  Args:
      api:  flask_restful Api object.
      path: string path for current resource. Example: 'api/testsruns/<int:id>/log'
  """
  # registers log as an api resource
  api.add_resource(Log, path)
  # directly add sub-resources of log <HERE>
