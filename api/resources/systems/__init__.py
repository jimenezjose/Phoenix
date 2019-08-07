from .hostnameStatus import HostnameStatus
from api.db import (
    execute_sql,
    get_hostnames_table)

from flask_restful import Resource, reqparse

class Systems(Resource):
  """System resource for hostnames organization and details."""

  def get(self):
    """GET request for all systems.

    Returns:
        A list of systems (hostnames) in the database. Also,
        Status Code 200 OK.
    """
    # query for hostnames with their status
    hostnames_table = get_hostnames_table()

    #response = {'hostnames' : {HOSTNAME_STATUS_ACTIVE : [], HOSTNAME_STATUS_RETIRED : []}}
    response = {'hostnames' : hostnames_table}

    return response, 200
 
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
