from .testHistory import TestHistory
from api.db import (
    execute_sql,
    validate_hostname_status,
    validate_hostname,
    get_hostnames,
    to_retiredflag)

from flask_restful import Resource

class Hostname(Resource):
  """Isolate a specific systems/hostname for info."""

  def get(self, hostname_status, hostname):
    """GET request for information about hostname

    Args:
        hostname_status: binary representation of a retired system.
        hostname: string name of system hostname passed through url.

    Returns:
        Success:
            * (valid query for an existing hostname)
                Status Code: 200 OK
        Failure:
            * (unkown status priovided) - therefore incorrect url provided
            * (hostname did not exist in the database)
                Status Code: 404 Not Found
    """
    validate_hostname_status(hostname_status)
    retiredflag = to_retiredflag(hostname_status)
    validate_hostname(hostname, retiredflag)

    # query for hostname information
    hostnames_list = get_hostnames(hostname, retiredflag)

    return {'hostnames' : hostnames_list} 

    return hostname_info

    return {'message' : 'Info on {} {} with id: {}'.format(hostname_status, hostname, records)}, 200

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
    TestHistory.add_all_resources(api, '{}/history'.format(path))
