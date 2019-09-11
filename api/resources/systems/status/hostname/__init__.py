from .history import TestHistory
from api.db import (
    get_table,
    validate)

from flask_restful import Resource

class Hostname(Resource):
  """Isolate a specific systems/hostname for info."""

  def get(self, hostname_status, hostname):
    """GET request for information about hostname

    Args:
        hostname_status: binary representation of a retired system.
        hostname: string name of system hostname passed through url.

    Returns:
        Hostname data as represented in the hostnames table.

        Success:
            Status Code: 200 OK
                * return hostnames table entry.
        Failure:
            Status Code: 404 Not Found
                * hostname does not exist or invalid hostname_status.
    """
    validate(hostname=hostname, hostname_status=hostname_status, http_error_code=404)    
    # query for hostname information
    hostnames_list = get_table('hostnames', hostname=hostname, hostname_status=hostname_status)

    return {'hostnames' : hostnames_list}, 200

  @staticmethod  
  def add_all_resources(api, path):
    """Recursively adds all sub-resources in the 'hostname' resource.

    Args:
        api:  flask_restful Api object.
        path: string path for current resource. Example: 'api/systems/<string:hostname>'
    """
    # register hostname as an api resource
    api.add_resource(Hostname, path)
    # directly add sub-resources of hostname
    TestHistory.add_all_resources(api, '{}/test-history'.format(path))
