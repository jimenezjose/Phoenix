from .test import Test

from flask_restful import Resource
from api.db import get_db

def add_all_resources(api, path):
  """Recursively adds all sub-resources in the 'hostname' resource.

  Args:
      api:  flask_restful Api object.
      path: string path for current resource. Example: 'api/systems/<string:hostname>'
  """
  api.add_resource(Hostname, path)
  Hostname.add_all_resources(api, path)

class Hostname(Resource):
  """Hostname resource with class design inhereted from flask_restful Resource."""

  def get(self, hostname):
    """Get information about hostname

    Args:
        hostname: string name of system hostname passed through url.
    """
    db = get_db()
    cursor = db.cursor()

    # query for hostname
    sql_query = 'SELECT id FROM hostnames WHERE hostname = %s'
    values = (hostname,)
    cursor.execute(sql_query, values)
    records = cursor.fetchall()

    if not records:
      # if no records exist for hostname, return 404 error.
      return {'message' : 'Hostname: {} not found.'.format(hostname)}, 404

    return {'message' : 'Info on: {} with id: {}'.format(hostname, records)}, 200

  def delete(self, hostname):
    """Deletes the hostname by setting the retired flag to True.

    Args:
        hostname: string name of system hostname passed through url.
    """
    db = get_db()
    cursor = db.cursor()

    # query for hostname
    sql_query  = 'SELECT id FROM hostnames WHERE hostname = %s AND retired = "0"'
    values = (hostname,)
    cursor.execute(sql_query, values)
    records = cursor.fetchall()

    if not records:
      # if no records exist for hostname, return 404 error.
      return {'message' : 'Hostname: {} not found.'.format(hostname)}, 404

    # otherwise update hostname and set its retired flag to true
    sql_update = 'UPDATE hostnames SET retired = "1" WHERE hostname = %s AND retired = "0"'
    values = (hostname,)
    cursor.execute(sql_update, values)
    db.commit()

    return {'message' : 'DELETE hostname: %s (set as retured with id: %d)' % (hostname, records)}, 200

  @staticmethod
  def add_all_resources(api, path):
    """Directly adds the necessary sub-resources.

    Args:
        api:  flask_restful Api object.
        path: string path for current resource. Example: 'api/systems/<string:hostname>'
    """ 
    Test.add_all_resources(api, '{}/test'.format(path))
