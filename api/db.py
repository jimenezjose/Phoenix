# tests_runs status to status_id TODO
# validate tests_runs_status
# single valide function with optional params
# look up by tests_name
import mysql.connector
import click
from flask import current_app, g
from flask.cli import with_appcontext
from flask_restful import abort

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

def execute_sql(command, db_commit=False, dictionary=True):
  """Executes a single sql command on the database.
  
  Args:
      command: mysql command.
      db_commit: inserting data into the database. 

  Returns:
      if db_commit is False then return the last row id inserted into a db table.
      otherwise return a list of dictionaries corresponding to the db table queried.
  """
  db = get_db()
  cursor = db.cursor(dictionary=dictionary)

  cursor.execute(command)

  if db_commit is True:
    db.commit()
    return cursor.lastrowid

  return cursor.fetchall()

def validate_hostname_status(hostname_status, http_error_code=404):
  """Validates hostname status to be 'active' or 'retired'.
  
  Args:
      hostname_status: binary representation of a hostnmame's status 
      http_error_code: status code returned if error is encountered.

  Raises:
      HTTPException: retiredflag is not valid, raises http_error_code.
  """
  errors = {}
  
  if not is_active(hostname_status) and not is_retired(hostname_status):
    errors.update({'hostname_status' : 'Provided hostname status \'{}\' is not valid.'.format(hostname_status)})

  if errors:
    abort(http_error_code, message=errors)

def validate_retiredflag(retiredflag, http_error_code=404):
  """Validates retiredflag is active '0' or 'retired '1'.
  
  Args:
      retiredflag: binary representation of a hostnmame's status 
      http_error_code: status code returned if error is encountered.

  Raises:
      HTTPException: retiredflag is not valid, raises http_error_code.
  """
  errors = {}

  if not is_active(retiredflag) and not is_retired(retiredflag):
    errors.update({'retiredflag' : 'Provided flag \'{}\' is not valid.'.format(retiredflag)})

  if errors:
    abort(http_error_code, message=errors)

def validate_hostname(hostname, retiredflag, http_error_code=404):
  """Validates hostname's existence in the database
  
  Args:
      hostname: string that represents a unique system.
      retiredflag: string that represents a system status.
      http_error_code: status code returned if error is encountered.

  Raises:
      HTTPException: hostname does not exist in the database as statusflag, raise http_error_code 
  """
  validate_retiredflag(retiredflag)
  hostname_status = to_hostname_status(retiredflag)
  errors = {}

  records = execute_sql("""
      SELECT hostname FROM hostnames 
      WHERE hostname = '{}' AND retired = '{}'
   """.format(hostname, retiredflag))

  if not records:
    # no existing hostname in database
    errors.update({'hostname' : '{} hostname \'{}\' Not Found.'.format(hostname_status, hostname)})
  
  if errors:
    abort(http_error_code, message=errors)

def validate_tests_name(tests_name, http_error_code=404):
  """Validates tests.name existence in the database
  
  Args:
      hostname: string that represents a unique system.
      retiredflag: string that represents a system status.
      http_error_code: status code returned if error is encountered.

  Raises:
      HTTPException: hostname does not exist in the database as statusflag, raise http_error_code 
  """
  errors = {}

  records = execute_sql("""
      SELECT * FROM tests 
      WHERE tests.name = '{}'
  """.format(tests_name))

  if not records:
    # no existing tests.name in the database
    errors.update({'tests_name' : '\'{}\' Not Found.'.format(tests_name)})

  if errors:
    abort(http_error_code, message=errors)

def validate_status_name(status_name):
  return

def validate_status_id(status_id):
  return

def get_hostnames_table(retiredflag=None):
  """GET all hostnames with the given retiredflag.
  
  Args:
      retiredflag: Optional argument that represents if the systems is retired or active. 
                   If retired is not passed in function call, retiredflag will act as a wildcard.
  """
  sql_command = """
      SELECT id, hostname, retired
      FROM hostnames
  """

  if retiredflag is not None:
    # query hostnames only with the given retiredflag 
    validate_retiredflag(retiredflag)
    sql_command = """
        {} WHERE retired = '{}'
    """.format(sql_command, retiredflag)

  hostnames_table = execute_sql(sql_command)

  return hostnames_table

def get_tests_runs_queue(hostname=None):
  """GET tests_runs_queue with optional constraint parameter - hostname."""
  # query for all tests runs in the queue
  sql_command =  """
      SELECT hostnames.hostname 
      FROM hostnames, tests_runs, tests_runs_queue
      WHERE hostnames.id = tests_runs.hostnames_id
      AND tests_runs.id = tests_runs_queue.test_runs_id
      AND tests_runs.status = '{}'
      AND hostnames.retired = '{}'
  """.format(STATUS_SCHEDULED, HOSTNAME_ACTIVE)

  if hostname is not None:
    # query for queued tests runs on the given hostname
    validate_hostname(hostname, HOSTNAME_ACTIVE)
    sql_command = """
        {} AND hostnames.hostname = '{}'
    """.format(sql_command, hostname)

  tests_runs_queue_table = execute_sql(sql_command)

  return tests_runs_queue_table

def get_tests_runs_table(hostname=None, status_id=None, status_name=None, tests_name=None):
  """Gets tests_runs_table with optional constraint paramters."""
  HOSTNAME_INDEX = 0
  TESTS_NAME_INDEX = 1
  STATUSES_INDEX = 2
  START_TIMESTAMP_INDEX = 3
  END_TIMESTAMP_INDEX = 4
  NOTES_INDEX = 5
  CONFIG_INDEX = 6
  SCRATCH_INDEX = 7
  ID_INDEX = 8

  # query for all running tests
  sql_command = """
      SELECT hostnames.hostname, tests.name, statuses.name, tests_runs.start_timestamp, 
          tests_runs.end_timestamp, tests_runs.notes, tests_runs.config, tests_runs.scratch,
          tests_runs.id
      FROM hostnames, tests, tests_runs, statuses
      WHERE hostnames.id = tests_runs.hostnames_id 
      AND tests.id = tests_runs.tests_id
      AND statuses.id = tests_runs.status
  """
  
  if hostname is not None:
    # query only tests under given hostname
    validate_hostname(hostname, HOSTNAME_ACTIVE)
    sql_command = """
        {} AND hostnames.hostname = '{}'
    """.format(sql_command, hostname)

  if status_id is not None:
    # query only tests with given status id
    validate_status_id(status_id)
    sql_command = """
        {} AND statuses.id = '{}'
    """.format(sql_command, status_id)

  if status_name is not None:
    # only query tests with given status name
    status_name = status_name.upper()
    validate_status_name(status_name)
    sql_command = """
        {} AND statuses.name = '{}'
    """.format(sql_command, status_name)

  if tests_name is not None:
    # query only for tests with the given tests name
    validate_tests_name(tests_name)
    sql_command = """
        {} AND tests.name = '{}'
    """.format(sql_command, tests_name)

  # get raw data (reason: key naming collision with tests.name and statuses.name)
  records = execute_sql(sql_command, dictionary=False)

  if not records:
    # no running tests
    return {}

  tests_runs_table = []
  for data in records:
    # datetime.datetime is not json serializable
    start_timestamp = str(data[START_TIMESTAMP_INDEX])
    end_timestamp = str(data[END_TIMESTAMP_INDEX])
    # follow consistency in representation of null objects
    if data[START_TIMESTAMP_INDEX] is None:
      start_timestamp = None
    if data[END_TIMESTAMP_INDEX] is None:
      end_timestamp = None
  
    tests_runs_table.append({
        'hostname' : data[HOSTNAME_INDEX],
        'tests_name' : data[TESTS_NAME_INDEX],
        'statuses_name' : data[STATUSES_INDEX],
        'start_timestamp' : start_timestamp,
        'end_timestamp' : end_timestamp,
        'notes' : data[NOTES_INDEX],
        'config' : data[CONFIG_INDEX],
        'scratch' : data[SCRATCH_INDEX],
        'id' : data[ID_INDEX]
    })

  return tests_runs_table

def get_running_tests(hostname=None):
  """GET currently running tests_runs on given hostname.

    Args:
        hostname: system hostname if none query as wildcard.
  """
  HOSTNAME_INDEX = 0
  TESTS_NAME_INDEX = 1
  STATUSES_INDEX = 2
  START_TIMESTAMP_INDEX = 3
  END_TIMESTAMP_INDEX = 4
  NOTES_INDEX = 5
  CONFIG_INDEX = 6
  SCRATCH_INDEX = 7

  # query for all running tests
  sql_command = """
      SELECT hostnames.hostname, tests.name, statuses.name, tests_runs.start_timestamp, 
          tests_runs.end_timestamp, tests_runs.notes, tests_runs.config, tests_runs.scratch
      FROM hostnames, tests, tests_runs, statuses
      WHERE tests_runs.end_timestamp = '{}'
      AND hostnames.id = tests_runs.hostnames_id 
      AND tests.id = tests_runs.tests_id
      AND statuses.id = tests_runs.status
      AND tests_runs.status = '{}'
      AND hostnames.retired = '{}'
  """.format(NULL_TIMESTAMP, STATUS_RUNNING, HOSTNAME_ACTIVE)
  
  if hostname is not None:
    # query only running tests on given hostname
    validate_hostname(hostname, HOSTNAME_ACTIVE)
    sql_command = """
       {} AND hostnames.hostname = '{}'
    """.format(sql_command, hostname)

  # get raw data (reason: key naming collision with tests.name and statuses.name)
  records = execute_sql(sql_command, dictionary=False)

  if not records:
    # no running tests
    return {}

  data = records[0]

  # datetime.datetime is not json serializable
  start_timestamp = str(data[START_TIMESTAMP_INDEX])
  end_timestamp = str(data[END_TIMESTAMP_INDEX])

  # follow consistency in representation of null objects
  if data[START_TIMESTAMP_INDEX] is None:
    start_timestamp = None
  if data[END_TIMESTAMP_INDEX] is None:
    end_timestamp = None
  
  running_tests = {
      'hostname' : data[HOSTNAME_INDEX],
      'tests_name' : data[TESTS_NAME_INDEX],
      'statuses_name' : data[STATUSES_INDEX],
      'start_timestamp' : start_timestamp,
      'end_timestamp' : end_timestamp,
      'notes' : data[NOTES_INDEX],
      'config' : data[CONFIG_INDEX],
      'scratch' : data[SCRATCH_INDEX]
  }

  return running_tests

def get_hostnames(hostname, retiredflag=None):
  """Gets hostname rows by hostname and with an optional retiredflag constraint."""
  # query for hostname
  sql_command = """
      SELECT id, hostname, retired
      FROM hostnames
      WHERE hostname = '{}'
  """.format(hostname)

  if retiredflag is not None:
    # only query for hostname with given retiredflag
    sql_command = """
        {} AND retired = '{}'
    """.format(sql_command, retiredflag)

  # list of hostnames that follow the criteria
  hostname_row_list = execute_sql(sql_command)

  return hostname_row_list

def get_hostname_by_id(id):
  """Gets hostnames row by row id in hostnames table."""
  # query hostname id 
  hostname_row_list = execute_sql("""
    SELECT id, hostname, retired
    FROM hostnames
    WHERE id = '{}'
  """.format(id))

  # there is only one hostname with the given unique id
  hostname_row = None
  if hostname_row_list:
    # valid id passed
    hostname_row = hostname_row_list[0]

  return hostname_row

def is_retired(flag):
  return flag == HOSTNAME_RETIRED or flag == HOSTNAME_STATUS_RETIRED

def is_active(flag):
  return flag == HOSTNAME_ACTIVE or flag == HOSTNAME_STATUS_ACTIVE

def to_retiredflag(hostname_status):
  """Convers hostnames_status to an equivalent retiredflag string"""
  if is_retired(hostname_status):
    return HOSTNAME_RETIRED

  return HOSTNAME_ACTIVE

def to_hostname_status(retiredflag):
  """Converts retiredflag to a hostname status strings {'active', 'retired'}"""
  if is_retired(retiredflag):
    return HOSTNAME_STATUS_RETIRED

  return HOSTNAME_STATUS_ACTIVE
