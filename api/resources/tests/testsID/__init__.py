from api.db import execute_sql

from flask_restful import Resource

class TestsID(Resource):
  """TestsID Resource that retrieves id specific test information."""
  def get(self, id):
    """GET request test information on given id."""

    # query info on test 'id': (test name, command name, command)
    records = execute_sql("""
        SELECT tests.name, commands.name, commands.command
        FROM tests, tests_commands, commands
        WHERE tests.id = %s 
        AND tests_commands.tests_id = tests.id
        AND tests_commands.commands_id = commands.id 
    """)

    return {'message' : 'test with id: {}, info: {}'.format(id, records)}

  @staticmethod
  def add_all_resources(api, path):
    """Recursively adds all sub-resources in the 'tests/<int:id>' resource.

    Args:
        api:  flask_restful Api object.
        path: string path for current resource. Example: 'api/tests/2'
    """
    # register 'tests/<int:id>' as an api resource
    api.add_resource(TestsID, path)
    # directly add sub-resources of 'tests/<int:id>' <HERE>
