from api.db import (
    execute_sql,
    HOSTNAME_RETIRED)
from api.resources.systems.statusflag.utils import (
    validate_systems_statusflag,
    to_retiredflag)
from .test import Test

from flask_restful import Resource

class Hostname(Resource):
  """Isolate a specific systems/hostname for info."""

  def get(self, statusflag, hostname):
    """GET request for information about hostname

    Args:
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
    validate_systems_statusflag(statusflag)
    retiredflag = to_retiredflag(statusflag)

    # query for hostname
    records = execute_sql("""
        SELECT id FROM hostnames 
        WHERE hostname = '{}' AND retired = '{}'
    """.format(hostname, retiredflag))

    if not records:
      # if no records exist for hostname, return 404 error.
      return {'message' : '{} Hostname: {}, Not Found.'.format(statusflag, hostname)}, 404

    return {'message' : 'Info on: {} with id: {}'.format(hostname, records)}, 200

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
