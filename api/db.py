import mysql.connector
import click
from flask import current_app, g
from flask.cli import with_appcontext

# tests_runs constants
NULL_TIMESTAMP = '0000-00-00 00:00:00'

# retired flags
HOSTNAME_RETIRED = '1'
HOSTNAME_ACTIVE  = '0'

# statuses
STATUS_PASSED = 1
STATUS_FAILED = 2
STATUS_COMPLETED = 3
STATUS_INCOMPLETED = 4
STATUS_RUNNING = 5
STATUS_IN_SHELL = 6
STATUS_SCHEDULED = 7
STATUS_STARTED = 8

def get_db():
  """Getter method to retrieve the current database connection.
    
  Returns:
      A mysql database connection corresponding with host, database, 
      and port as configured below.
  """
  if 'db' not in g:
    g.db = mysql.connector.connect(
        host = 'localhost',
        user = 'root',
        passwd = 'Jose88',
        database = 'TestPhoenix',
        port = 3306
    )
  return g.db     

def close_db(error):
  """Closes the database connection."""
  db = g.pop('db', None)

  if db is not None:
    db.close()

def init_app(app):
  """Binds the cloe_db function to be invoked upon app closure."""
  app.teardown_appcontext(close_db)

def execute_sql(command, db_commit=False):
  """Insert into the mysql database.
  
  Args:
      insert_str: string sql command to executed.

  Returns:
      The last row id affected by the sql insert command.
  """
  db = get_db()
  cursor = db.cursor()

  cursor.execute(command)

  if db_commit is True:
    db.commit()
    return cursor.lastrowid

  return cursor.fetchall()

