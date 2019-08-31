from .hostnameStatus import HostnameStatus
from api.db import get_table
from flask_restful import (
    Resource, 
    reqparse)

class Systems(Resource):
  """System resource for hostnames organization and details."""

  def get(self):
    """GET request for all systems.

    Returns:
        Dictionary of data in hostnames table.

        Success:
            Status Code: 200 OK
                * hostnames table returned.
    """
    # query for all hostnames in the database
    hostnames_table = get_table('hostnames')

    return {'hostnames' : hostnames_table}, 200
 
  @staticmethod
  def add_all_resources(api, path):
    """Recursively adds all sub-resources in the 'system' resource.

    Args:
        api:  flask_restful Api object.
        path: string path for current resource. Example: 'api/systems'
    """
    # register systems as an api resource
    api.add_resource(Systems, path)
    # directly add sub-resources of system
    HostnameStatus.add_all_resources(api, '{}/<string:hostname_status>'.format(path))
