from api.db import (
    execute_sql,
    HOSTNAME_RETIRED)
from .hostname import Hostname
from .utils import (
    validate_systems_statusflag,
    is_active,
    is_retired,
    to_retiredflag)

from flask_restful import Resource, reqparse

class Statusflag(Resource):
  """Statusflag that annotates a hostname system as 'retired' or 'active'."""

  def get(self, statusflag):
    """GET request for all systems labeled as 'statusflag' = {retired, active}
    
    Args:
        statusflag: string annotation of a system for a binary representation of an 'active' or 
                    'retired' hostname.
    
    Returns:
        Success:
            * (valid statusflag provided)
                Status Flag: 200 OK
        Failure:
            * (statusflag provided unknown) - not {active, retired}
                Status Flag: 404 Not Found
    """
    validate_systems_statusflag(statusflag)
    retiredflag = to_retiredflag(statusflag)

    records = execute_sql("""
        SELECT hostname FROM hostnames
        WHERE retired = '{}'
    """.format(retiredflag))

    return {'message' : 'list of {} hostnames: {}'.format(statusflag, records)}, 200

  def post(self, statusflag):
    """POST request to add a hostname to the database.
    
    Returns:
        Success: 
            * (hostname inserted into the database)
                Status Code: 201 Created

        Failure: 
            * (statusflag provided does not exist)
                Status Code: 404 Not Found
            * (attempt to add a non-active hostname not allowed)
                Status Code: 405 Method Not Allowed
            * (required arguments not supplied in request) - implicit return by reqparse.
                Status Code: 404 Not Found
            * (duplicate insertion for active hostname not allowed) 
                Status Code: 409 Conflict
    """
    parser = reqparse.RequestParser()
    validate_systems_statusflag(statusflag)
    retiredflag = to_retiredflag(statusflag)

    # require 'hostname' parameter from request. 
    parser.add_argument('hostname', required=True)
    args = parser.parse_args()

    if not is_active(statusflag):
      # Hostnames added to the database must be active, return status code 405 Method Not Allowed
      return {'message' : 'Hostname must initially be active to be added to the database'}, 405

    # check if working hostname already exists in db.
    records = execute_sql("""
        SELECT hostname FROM hostnames
        WHERE retired = '{}' AND hostname = '{}'
    """.format(retiredflag, args['hostname']))

    if records:
      # active hostname already exists, returning conflict status code 409.
      return {'message' : 'active hostname, {}, already exists'.format(args['hostname'])}, 409

    # otherwise, insert hostname into db.
    execute_sql("""
        INSERT INTO hostnames 
        (hostname) VALUES ('{}')
    """.format(args['hostname']), db_commit=True)

    return {'message' : 'inserted: {}'.format(args['hostname'])}, 201

  def delete(self, statusflag):
    """DELETE the hostname by setting the retired flag to True.

    Args:
        hostname: string name of system hostname passed through url.
    """
    parser = reqparse.RequestParser()
    validate_systems_statusflag(statusflag)
    retiredflag = to_retiredflag(statusflag)

    # require 'hostname' parameter from request. 
    parser.add_argument('hostname', required=True)
    args = parser.parse_args()

    if not is_active(statusflag):
        # Only remove active hostnames; return 405 Method Not Allowed
        return {'message' : 'The method is not allowed for the requested URL.'}, 405

    # query for hostname
    records = execute_sql("""
        SELECT id FROM hostnames 
        WHERE hostname = '{}' AND retired = '{}'
    """.format(args['hostname'], retiredflag))

    if not records:
      # if no records exist for hostname, return 404 error.
      return {'message' : 'Hostname: {}, Not Found.'.format(args['hostname'])}, 404

    # otherwise update hostname and set its retired flag to true
    execute_sql("""
        UPDATE hostnames 
        SET retired = '{}' 
        WHERE hostname = '{}' AND retired = '{}'
    """.format(HOSTNAME_RETIRED, args['hostname'], retiredflag), db_commit=True)

    return {'message' : 'DELETE hostname: {} (set as retired with id: {})'.format(args['hostname'], records)}, 200

  
  @staticmethod  
  def add_all_resources(api, path):
    """Recursively adds all sub-resources in the 'system/<string:statusflag>' resource.

    Args:
        api:  flask_restful Api object.
        path: string path for current resource. Example: 'api/systems/active'
    """
    # register systems as an api resource
    api.add_resource(Statusflag, path)
    # directly add sub-resources of systems/<string:statusflag>
    Hostname.add_all_resources(api, '{}/<string:hostname>'.format(path))
