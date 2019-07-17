from api.db import get_db
from .test import Test

from flask_restful import Resource

class Hostname(Resource):
  """Hostname resource with class design inhereted from flask_restful Resource."""

  def get(self, hostname):
    """GET request for information about hostname

    Args:
        hostname: string name of system hostname passed through url.
    """
    db = get_db()
    cursor = db.cursor()

    # query for hostname
    sql_query = """
        SELECT id FROM hostnames 
        WHERE hostname = %s AND retired = '0'
    """
    values = (hostname,)
    cursor.execute(sql_query, values)
    records = cursor.fetchall()

    if not records:
      # if no records exist for hostname, return 404 error.
      return {'message' : 'Hostname: {} not found.'.format(hostname)}, 404

    return {'message' : 'Info on: {} with id: {}'.format(hostname, records)}, 200

  def delete(self, hostname):
    """DELETE the hostname by setting the retired flag to True.

    Args:
        hostname: string name of system hostname passed through url.
    """
    db = get_db()
    cursor = db.cursor()

    # query for hostname
    sql_query  = """
        SELECT id FROM hostnames 
        WHERE hostname = %s AND retired = '0'
    """
    values = (hostname,)
    cursor.execute(sql_query, values)
    records = cursor.fetchall()

    if not records:
      # if no records exist for hostname, return 404 error.
      return {'message' : 'Hostname: {} not found.'.format(hostname)}, 404

    # otherwise update hostname and set its retired flag to true
    sql_update = """
        UPDATE hostnames 
        SET retired = '1' 
        WHERE hostname = %s AND retired = '0'
    """
    values = (hostname,)
    cursor.execute(sql_update, values)
    db.commit()

    return {'message' : 'DELETE hostname: {} (set as retired with id: {})'.format(hostname, records)}, 200

def add_all_resources(api, path):
  """Recursively adds all sub-resources in the 'hostname' resource.

  Args:
      api:  flask_restful Api object.
      path: string path for current resource. Example: 'api/systems/<string:hostname>'
  """
  # register hostname as an api resource
  api.add_resource(Hostname, path)
  # directly add sub-resources of hostname
  Test.add_all_resources(api, '{}/test'.format(path))
