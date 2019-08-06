from .hostnameStatus import HostnameStatus
from api.db import (
    execute_sql,
    is_retired,
    HOSTNAME_STATUS_ACTIVE,
    HOSTNAME_STATUS_RETIRED)

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
    records = execute_sql('SELECT hostname, retired FROM hostnames')

    json_dict = {'hostnames' : {HOSTNAME_STATUS_ACTIVE : [], HOSTNAME_STATUS_RETIRED : []}}

    active_list = []
    retired_list = []
    for server in records:
      # categorize hostnames to retired/active bucket lists
      hostname = server[0] 
      retiredflag = server[1]

      if is_retired(retiredflag):
        retired_list.append(hostname)
      else:
        active_list.append(hostname)

    json_dict['hostnames'][HOSTNAME_STATUS_ACTIVE] = active_list
    json_dict['hostnames'][HOSTNAME_STATUS_RETIRED] = retired_list

    return json_dict, 200
 
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
