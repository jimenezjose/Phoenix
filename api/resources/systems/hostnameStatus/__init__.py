# NOTE DELETE CANNOT OCCUR IF HOSTNAME HAS RUNNING OR QUEUED TESTS.
# TODO delet by hostname id optional argument in delete request
from .hostname import Hostname
from api.db import (
    execute_sql,
    HOSTNAME_RETIRED,
    HOSTNAME_ACTIVE,
    validate_hostname_status,
    validate_hostname,
    get_hostnames,
    get_hostname_by_id,
    validate,
    get_table,
    delete_hostname,
    insert_hostname,
    is_retired,
    to_retiredflag)

from flask_restful import Resource, reqparse, abort

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
    validate(hostname_status=hostname_status)

    # Get all hostnames with given retired hostname status
    hostnames_table = get_table('hostnames', hostname_status=hostname_status)

    return {'hostnames' : hostnames_table}, 200

  def post(self, hostname_status):
    """POST request to add a hostname to the database.
    
    Args:
        hostname_status: string annotation of a system for a binary representation of an 'active' 

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
    validate(hostname_status=hostname_status)

    # require 'hostname' parameter from request. 
    parser = reqparse.RequestParser()
    parser.add_argument('hostname', required=True)
    args = parser.parse_args()

    if is_retired(hostname_status):
      # Hostnames added to the database must be active, return status code 405 Method Not Allowed
      return {'message' : 'The method is not allowed for the requested URL.'}, 405

    # check if working hostname already exists in db.
    existing_hostname = get_table('hostnames', hostname=args['hostname'], hostname_status=hostname_status) 

    if existing_hostname:
      # active hostname already exists, returning conflict status code 409.
      return {'message' : '{} hostname, {}, already exists. Insertion not allowed.'.format(hostname_status, args['hostname'])}, 409

    # otherwise, insert hostname into db.
    inserted_hostname = insert_hostname(args['hostname'])

    return inserted_hostname

  def delete(self, hostname_status):
    """DELETE the hostname by setting the retired flag to True."""
    if is_retired(hostname_status):
        # only remove active hostnames; return 405 Method Not Allowed
        return {'message' : 'The method is not allowed for the requested URL.'}, 405

    # require 'hostname' parameter from request. 
    parser = reqparse.RequestParser()
    parser.add_argument('hostname', type=str)
    parser.add_argument('hostname_id', type=int)
    args = parser.parse_args()

    if args['hostname'] is None and args['hostname_id'] is None:
      # at least one argument is required otherwise throw 400 Bad Request.
      errors = {
          'hostname' : 'Missing parameter in JSON body',
          'hostname_id' : 'Missing parameter in JSON body',
          'message' : 'At least one paramter is required.',
      }
      abort(400, message=errors)

    # validate url hostname status
    validate(hostname_status=hostname_status, http_error_code=404)
    # `
    validate(hostname=args['hostname'], hostname_id=args['hostname_id'], http_error_code=400)

    if args['hostname_id']:
      return delete_hostname(hostname_id=args['hostname_id'])
    elif args['hostname']:
      return delete_hostname(hostname=args['hostname'])

    # get all info on VALID hostname of interest. 
    hostname_list = get_hostnames(args['hostname'], HOSTNAME_ACTIVE)
    # only one unique ACTIVE hostname will exist guaranteed.
    hostname_row = hostname_list[0]
    
    return 'error'

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
