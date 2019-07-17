from api.db import get_db
from .hostname import Hostname

from flask_restful import Resource, reqparse

class Systems(Resource):
  """System resource with class design inherited from flask_restful Resource."""

  def get(self):
    """GET request for all unretired systems."""
    db = get_db()
    cursor = db.cursor()

    # query for unretired hostnames
    sql_query = 'SELECT hostname FROM hostnames WHERE retired = "0"'
    cursor.execute(sql_query)
    records = cursor.fetchall()

    return {'message' : 'list of unretired hostnames: {}'.format(records)}, 200

  def post(self):
    """POST request to add a hostname to the database.
    
    Returns:
        Success: 
            * (hostname inserted into the database)
                Status Code: 201 Created

        Failure: 
            * (required arguments not supplied in request) - implicit return by reqparse.
                Status Code: 404 Not Found
            * (duplicate insertion for unretired hostname not allowed) 
                Status Code: 409 Conflict
    """
    db = get_db()
    cursor = db.cursor()
    parser = reqparse.RequestParser()

    # require 'hostname' parameter from request. 
    parser.add_argument('hostname', required=True) 
    args = parser.parse_args()

    # check if working hostname already exists in db.
    sql_query = 'SELECT hostname FROM hostnames WHERE retired = "0" AND hostname = %s'
    values = (args['hostname'],)
    cursor.execute(sql_query, values)
    records = cursor.fetchall()

    if records:
      # unretired hostname already exists, returning conflict status code 409.
      return {'message' : 'unretired hostname, {}, already exists'.format(args['hostname'])}, 409

    # otherwise, insert hostname into db.
    sql_insert = 'INSERT INTO hostnames (hostname) VALUES (%s)'
    values = (args['hostname'],)
    cursor.execute(sql_insert, values)
    db.commit()

    return {'message' : 'inserted: {}'.format(str(args['hostname']))}, 201

def add_all_resources(api, path):
  """Recursively adds all sub-resources in the 'system' resource.

  Args:
      api:  flask_restful Api object.
      path: string path for current resource. Example: 'api/systems'
  """
  # register systems as an api resource
  api.add_resource(Systems, path)
  # directly add sub-resources of system
  Hostname.add_all_resources(api, '{}/<string:hostname>'.format(path))
