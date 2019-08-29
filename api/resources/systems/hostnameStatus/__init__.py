# NOTE DELETE CANNOT OCCUR IF HOSTNAME HAS RUNNING OR QUEUED TESTS.
# TODO delet by hostname id optional argument in delete request
from .hostname import Hostname
from api.db import (
    validate,
    get_table,
    delete_hostname,
    insert_hostname,
    get_running_tests,
    is_retired)

from flask_restful import (
    Resource, 
    reqparse, 
    abort)

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
    """DELETE the hostname by setting the retired flag to True.

    Args:
        hostname_status: string annotation of a system to show retired status. 

    Returns:
        List of deleted hostnames. 
    """
    # TODO return change documentation in future
    validate(hostname_status=hostname_status)

    if is_retired(hostname_status):
        # only remove active hostnames; return 405 Method Not Allowed
        return {'message' : 'The method is not allowed for the requested URL.'}, 405

    # require 'hostname' parameter from request. 
    parser = reqparse.RequestParser()
    parser.add_argument('hostname', type=str)
    parser.add_argument('hostnames_id', type=int)
    args = parser.parse_args()

    if args['hostname'] is None and args['hostnames_id'] is None:
      # at least one argument is required otherwise throw 400 Bad Request.
      errors = {
          'hostname' : 'Missing parameter in JSON body',
          'hostnames_id' : 'Missing parameter in JSON body',
          'message' : 'At least one paramter is required',
      }
      abort(400, message=errors)

    # validate that the active hostname exists in the db
    validate(
        hostname=args['hostname'], 
        hostnames_id=args['hostnames_id'], 
        http_error_code=400
    )

    return

    # if hostname is running tests abort request
    running_tests = get_running_tests(args['hostname'])

    if running_tests:
      # system currently running tests - throw 400 Bad Request.
      error_msg = 'System is Busy. Currently processing {} tests.'.format(len(running_tests))
      errors = {args['hostname'] : error_msg}
      abort(400, message=errors)

    # TODO CHANGE THIS TO NOT BE A LIST: PRELIMARY LIST FOR DEBUG AND DEVELOPING PURPOSES
    hostnames_deleted = []
    if args['hostnames_id']:
      hostnames_deleted = delete_hostname(hostnames_id=args['hostnames_id'])
    elif args['hostname']:
      hostnames_deleted = delete_hostname(hostname=args['hostname'])

    hostnames_deleted = delete_hostname(hostnames_id=args['hostnames_id'], hostname=args['hostname'])

    return {'hostnames' : hostnames_deleted}

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
