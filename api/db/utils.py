from datetime import datetime
from flask import g
from flask_restful import abort
import mysql.connector

# tests_runs constants
NULL_TIMESTAMP = '0000-00-00 00:00:00'
# retired flags
HOSTNAME_RETIRED = 'true'
HOSTNAME_ACTIVE  = 'false'
# retired flag status name
HOSTNAME_STATUS_ACTIVE = 'active'
HOSTNAME_STATUS_RETIRED = 'retired'
# statuses
STATUS_PASSED = 1
STATUS_FAILED = 2
STATUS_COMPLETED = 3
STATUS_INCOMPLETED = 4
STATUS_RUNNING = 5
STATUS_IN_SHELL = 6
STATUS_SCHEDULED = 7
STATUS_STARTED = 8
STATUS_QUEUED = 9
# STATIC DATATYPE TABLES
DATATYPE_TABLES = ['statuses', 'tests', 'commands', 'hostnames']

def init_app(app):
  """Binds the cloe_db function to be invoked upon app closure."""
  app.teardown_appcontext(close_db)

def execute_sql(command, db_commit=False, dictionary=True):
  """Executes a single sql command on the database.
  
  Args:
      command: mysql command.
      db_commit: inserting data into the database. 

  Returns:
      if db_commit is True then return the last row id inserted into a db table.
      otherwise return a list of dictionaries corresponding to the db table queried.
  """
  db = get_db()
  cursor = db.cursor(dictionary=dictionary)

  cursor.execute(command)

  if db_commit is True:
    db.commit()
    return cursor.lastrowid

  data = cursor.fetchall()
  return json_serialize(data)

def json_serialize(data):
  """Ensures data is JSON serializable for api requests.
  
  Args:
      data: list of database dictionaries/tuples of table rows.

  Note:
      This function mutates the original referenced list.
  """
  for index, row in enumerate(data):
    if isinstance(row, dict):
      # case I: data is a list of dictionaries
      for field, value in row.items():
        if value is None:
          continue
        if isinstance(value, datetime):
          data[index].update({field : str(value)})

    elif isinstance(row, tuple):
      # case II: data is a list of tuples
      mutable_row = list(row)
      for element_index, element in enumerate(row):
        if element is None:
          continue
        if isinstance(element, datetime):
          mutable_row[element_index] = str(element)
      data[index] = tuple(mutable_row)

  return data

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

def is_retired(flag):
  return flag == HOSTNAME_RETIRED or flag == HOSTNAME_STATUS_RETIRED

def is_active(flag):
  return flag == HOSTNAME_ACTIVE or flag == HOSTNAME_STATUS_ACTIVE

def to_retiredflag(hostname_status):
  """Convers hostnames_status to an equivalent retiredflag string"""
  if is_retired(hostname_status):
    return HOSTNAME_RETIRED
  elif is_active(hostname_status):
    return HOSTNAME_ACTIVE

  # error, return uncoverted string
  return hostname_status

def to_hostname_status(retiredflag):
  """Converts retiredflag to a hostname status strings {'active', 'retired'}"""
  if is_retired(retiredflag):
    return HOSTNAME_STATUS_RETIRED
  elif is_active(retiredflag):
    return HOSTNAME_STATUS_ACTIVE

  # error, return uncoverted string
  return retiredflag
