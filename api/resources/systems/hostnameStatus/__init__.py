from api.db import (
    execute_sql,
    HOSTNAME_RETIRED,
    HOSTNAME_ACTIVE,
    validate_hostname_status,
    validate_hostname,
    get_hostnames_table,
    get_hostname,
    get_hostname_by_id,
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

    hostnames_table = get_hostnames_table(retiredflag)

    return {'hostnames' : hostnames_table}, 200

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
    existing_hostname = get_hostname(args['hostname'], retiredflag)

    if existing_hostname:
      # active hostname already exists, returning conflict status code 409.
      return {'message' : '{} hostname, {}, already exists. Insertion not allowed.'.format(hostname_status, args['hostname'])}, 409

    # otherwise, insert hostname into db.
    rowid = execute_sql("""
        INSERT INTO hostnames 
        (hostname) VALUES ('{}')
    """.format(args['hostname']), db_commit=True)

    inserted_row = get_hostname_by_id(rowid)

    return inserted_row

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

    # get all info on VALID hostname of interest. 
    hostname_list = get_hostname(args['hostname'], HOSTNAME_ACTIVE)
    # only one unique ACTIVE hostname will exist guaranteed.
    hostname_row = hostname_list[0]

    # update active hostname to retired
    execute_sql("""
        UPDATE hostnames 
        SET retired = '{}' 
        WHERE hostname = '{}' AND retired = '{}'
    """.format(HOSTNAME_RETIRED, args['hostname'], HOSTNAME_ACTIVE), db_commit=True)

    # get updated hostname row 
    updated_hostname_row = get_hostname_by_id(hostname_row['id'])

    return updated_hostname_row

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
