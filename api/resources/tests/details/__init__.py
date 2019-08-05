from api.db import execute_sql

from flask_restful import Resource

class Details(Resource):
  """Resource: 'details' to get information about all tests.""" 

  def get(self):
    """GET request for all tests' info."""

    # query info (test name, command name, terminal command)
    records = execute_sql("""
        SELECT tests.name, commands.name, commands.command 
        FROM tests, tests_commands, commands
        WHERE tests.id = tests_commands.tests_id 
        AND tests_commands.commands_id = commands.id
    """)    

    return {'message' : 'tests details: (test name, command name, command): {}'.format(records)}

  @staticmethod
  def add_all_resources(api, path):
    """Recursively adds all sub-resources in the 'tests/details' resource.

    Args:
        api:  flask_restful Api object.
        path: string path for current resource. Example: 'api/tests/details'
    """
    # register 'tests/details' as an api resource
    api.add_resource(Details, path)
    # directly add sub-resources of 'details' <HERE>
