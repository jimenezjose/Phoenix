from api.db import get_db

from flask_restful import Resource

class TestsID(Resource):
  """TestsID Resource that retrieves id specific test information."""
  def get(self, id):
    """GET request test information on given id."""
    db = get_db()
    cursor = db.cursor()

    # query info on test 'id': (test name, command name, command)
    sql_query = """
        SELECT tests.name, commands.name, commands.command
        FROM tests, tests_commands, commands
        WHERE tests.id = %s 
        AND tests_commands.tests_id = tests.id
        AND tests_commands.commands_id = commands.id 
    """
    values = (id,)
    cursor.execute(sql_query, values)
    records = cursor.fetchall()

    return {'message' : 'test with id: {}, info: {}'.format(id, records)}

def add_all_resources(api, path):
  """Recursively adds all sub-resources in the 'tests/<int:id>' resource.

  Args:
      api:  flask_restful Api object.
      path: string path for current resource. Example: 'api/tests/2'
  """
  # register 'tests/<int:id>' as an api resource
  api.add_resource(TestsID, path)
  # directly add sub-resources of 'tests/<int:id>' <HERE>
