from api.db import (
    execute_sql,
    HOSTNAME_RETIRED,
    HOSTNAME_ACTIVE,
    validate_hostname_status,
    validate_hostname,
    is_retired,
    to_retiredflag)
from .hostname import Hostname

from flask_restful import Resource, reqparse

class HostnameStatus(Resource):
  """Statusflag that annotates a hostname system as 'retired' or 'active'."""

  def get(self, hostname_status):
    """GET request for all systems labeled as given by the 'hostname_status' 
    
    Args:
        hostname_status: string annotation of a system for a binary representation of an 'active' 
                         or 'retired' hostname.
    
    Returns:
        Success:
            * (valid status provided)
                Status Code: 200 OK
        Failure:
            * (status provided unknown) - not {active, retired}
                Status Code: 404 Not Found
    """
    validate_hostname_status(hostname_status)
    retiredflag = to_retiredflag(hostname_status) 

    records = execute_sql("""
        SELECT hostname FROM hostnames
        WHERE retired = '{}'
    """.format(retiredflag))

    response = {'hostnames' : {hostname_status : []}}

    hostname_list = []
    for server in records:
      hostname = server['hostname']
      hostname_list.append(hostname)

    response['hostnames'][hostname_status] = hostname_list

    return response, 200

  def post(self, hostname_status):
    """POST request to add a hostname to the database.
    
    Returns:
        Success: 
            * (hostname inserted into the database)
                Status Code: 201 Created

        Failure: 
            * (status provided does not exist)
                Status Code: 404 Not Found
            * (attempt to add a non-active hostname not allowed)
                Status Code: 405 Method Not Allowed
            * (required arguments not supplied in request) - implicit return by reqparse.
                Status Code: 404 Not Found
            * (duplicate insertion for active hostname not allowed) 
                Status Code: 409 Conflict
    """
    parser = reqparse.RequestParser()
    validate_hostname_status(hostname_status)
    retiredflag = to_retiredflag(hostname_status)
    
    # require 'hostname' parameter from request. 
    parser.add_argument('hostname', required=True)
    args = parser.parse_args()

    if is_retired(retiredflag):
      # Hostnames added to the database must be active, return status code 405 Method Not Allowed
      return {'message' : 'The method is not allowed for the requested URL.'}, 405

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

  def delete(self, hostname_status):
    """DELETE the hostname by setting the retired flag to True."""
    parser = reqparse.RequestParser()
    validate_hostname_status(hostname_status)
    retiredflag = to_retiredflag(hostname_status)

    # require 'hostname' parameter from request. 
    parser.add_argument('hostname', required=True)
    args = parser.parse_args()

    if is_retired(retiredflag):
        # only remove active hostnames; return 405 Method Not Allowed
        return {'message' : 'The method is not allowed for the requested URL.'}, 405

    # validate active hostname
    validate_hostname(args['hostname'], HOSTNAME_ACTIVE) 

    # update active hostname to retired
    rowid = execute_sql("""
        UPDATE hostnames 
        SET retired = '{}' 
        WHERE hostname = '{}' AND retired = '{}'
    """.format(HOSTNAME_RETIRED, args['hostname'], HOSTNAME_ACTIVE), db_commit=True)

    return {'message' : 'DELETE hostname: {} (set as retired with id: {})'.format(args['hostname'], rowid)}, 200

  
  @staticmethod  
  def add_all_resources(api, path):
    """Recursively adds all sub-resources in the 'system/<string:hostname_status>' resource.

    Args:
        api:  flask_restful Api object.
        path: string path for current resource. Example: 'api/systems/active'
    """
    # register systems as an api resource
    api.add_resource(HostnameStatus, path)
    # directly add sub-resources of systems/<string:hostname_status>
    Hostname.add_all_resources(api, '{}/<string:hostname>'.format(path))
