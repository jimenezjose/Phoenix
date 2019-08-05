from api.db import (
    execute_sql,
    HOSTNAME_RETIRED,
    HOSTNAME_ACTIVE)
from .hostname import Hostname
from api.resources.utils import (
    validate_retiredflag,
    validate_hostname,
    is_active,
    is_retired,
    to_hostname_status)

from flask_restful import Resource, reqparse

class Retiredflag(Resource):
  """Statusflag that annotates a hostname system as 'retired' or 'active'."""

  def get(self, retiredflag):
    """GET request for all systems labeled as given by the 'retiredflag' 
    
    Args:
        retiredflag: string annotation of a system for a binary representation of an active '0' or 
                     retired '1' hostname.
    
    Returns:
        Success:
            * (valid statusflag provided)
                Status Flag: 200 OK
        Failure:
            * (statusflag provided unknown) - not {active, retired}
                Status Flag: 404 Not Found
    """
    validate_retiredflag(retiredflag)
    hostname_status = to_hostname_status(retiredflag)

    records = execute_sql("""
        SELECT hostname FROM hostnames
        WHERE retired = '{}'
    """.format(retiredflag))

    return {'message' : 'list of {} hostnames: {}'.format(hostname_status, records)}, 200

  def post(self, retiredflag):
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
    validate_retiredflag(retiredflag)
    hostname_status = to_hostname_status(retiredflag)
    
    # require 'hostname' parameter from request. 
    parser.add_argument('hostname', required=True)
    args = parser.parse_args()

    if is_retired(retiredflag):
      # Hostnames added to the database must be active, return status code 405 Method Not Allowed
      return {'message' : 'Hostname must initially be active to be added to the database'}, 405

    # check if working hostname already exists in db.
    records = execute_sql("""
        SELECT hostname FROM hostnames
        WHERE retired = '{}' AND hostname = '{}'
    """.format(retiredflag, args['hostname']))

    if records:
      # active hostname already exists, returning conflict status code 409.
      return {'message' : '{} hostname, {}, already exists'.format(hostname_status, args['hostname'])}, 409

    # otherwise, insert hostname into db.
    execute_sql("""
        INSERT INTO hostnames 
        (hostname) VALUES ('{}')
    """.format(args['hostname']), db_commit=True)

    return {'message' : 'inserted: {}'.format(args['hostname'])}, 201

  def delete(self, retiredflag):
    """DELETE the hostname by setting the retired flag to True.

    Args:
        hostname: string name of system hostname passed through url.
    """
    parser = reqparse.RequestParser()
    validate_retiredflag(retiredflag)

    # require 'hostname' parameter from request. 
    parser.add_argument('hostname', required=True)
    args = parser.parse_args()

    if is_retired(retiredflag):
        # Only remove active hostnames; return 405 Method Not Allowed
        return {'message' : 'The method is not allowed for the requested URL.'}, 405

    # validate active hostname
    validate_hostname(args['hostname'], HOSTNAME_ACTIVE)

    # update active hostname to retired
    execute_sql("""
        UPDATE hostnames 
        SET retired = '{}' 
        WHERE hostname = '{}' AND retired = '{}'
    """.format(HOSTNAME_RETIRED, args['hostname'], HOSTNAME_ACTIVE), db_commit=True)

    return {'message' : 'DELETE hostname: {} (set as retired with id: {})'.format(args['hostname'], records)}, 200

  
  @staticmethod  
  def add_all_resources(api, path):
    """Recursively adds all sub-resources in the 'system/<string:statusflag>' resource.

    Args:
        api:  flask_restful Api object.
        path: string path for current resource. Example: 'api/systems/active'
    """
    # register systems as an api resource
    api.add_resource(Retiredflag, path)
    # directly add sub-resources of systems/<string:statusflag>
    Hostname.add_all_resources(api, '{}/<string:hostname>'.format(path))
