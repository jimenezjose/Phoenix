from .test import Test
from api.db import execute_sql
from api.resources.utils import (
    validate_retiredflag,
    validate_hostname,
    to_hostname_status)

from flask_restful import Resource

class Hostname(Resource):
  """Isolate a specific systems/hostname for info."""

  def get(self, retiredflag, hostname):
    """GET request for information about hostname

    Args:
        retiredflag: binary representation of a retired system.
        hostname: string name of system hostname passed through url.

    Returns:
        Success:
            * (valid query for an existing hostname)
                Status Code: 200 OK
        Failure:
            * (unkown statusflag priovided) - therefore incorrect url provided
            * (hostname did not exist in the database)
                Status Code: 404 Not Found
    """
    validate_retiredflag(retiredflag)
    validate_hostname(hostname, statusflag)
    hostname_status = to_hostname_status(retiredflag)

    # query for hostname information
    records = execute_sql("""
        SELECT id FROM hostnames 
        WHERE hostname = '{}' AND retired = '{}'
    """.format(hostname, retiredflag))

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
    Test.add_all_resources(api, '{}/test'.format(path))
