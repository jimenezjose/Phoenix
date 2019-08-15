# tests_runs status to status_id TODO
# validate tests_runs_status
# single valide function with optional params
# look up by tests_name
# validate arguments from JSON body given 400 error not 404. this is not a db problem rather and route handling prob.
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

def init_app(app):
  """Binds the cloe_db function to be invoked upon app closure."""
  app.teardown_appcontext(close_db)

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

  return cursor.fetchall()

def insert_hostname(hostname):
  """Inserts hostname to database."""
  rowid = execute_sql("""
      INSERT INTO hostnames 
      (hostname) VALUES ('{}')
  """.format(hostname), db_commit=True)
  return rowid

def delete_hostname(hostname=None, hostname_id=None):
  """Deletes hostnames by setting hostname.retired to true.""" 
  # to be deleted rows from hostnames table.
  deleted_rows = []

  if hostname is None and hostname_id is None:
    # require at least one parameter 
    return deleted_rows

  if hostname_id is not None:
    deleted_rows = get_hostnames_by_id(hostname_id) 
  elif hostname is not None:
    deleted_rows = get_hostnames(hostname, HOSTNAME_ACTIVE) 

  sql_command = """
      UPDATE hostnames
      SET retired = '{}'
      WHERE retired = '{}'
  """.format(HOSTNAME_RETIRED, HOSTNAME_ACTIVE)

  if hostname_id is not None:
    # delete hostname row by id
    sql_command = """
        {} AND id = '{}'
    """.format(sql_command, hostname_id)
  elif hostname is not None:
    # delete hostname by name
    sql_command = """
      {} AND hostname = '{}'
    """.format(sql_command, hostname)

  execute_sql(sql_command, db_commit=True)

  return deleted_rows

def validate(hostname=None, hostname_status=None, hostname_id=None, retiredflag=None, 
             tests_name=None, tests_runs_status=None, tests_runs_status_id=None, 
             table_name=None, http_error_code=404):
  """Validates system variables in the database."""
  
  if hostname is not None:
    validate_hostname(hostname, None, http_error_code)

  if hostname_status is not None:
    validate_hostname_status(hostname_status, http_error_code)

  if retiredflag is not None:
    validate_retiredflag(retiredflag, http_error_code)

  if tests_name is not None:
    validate_tests_name(tests_name, http_error_code)

  if tests_runs_status is not None:
    validate_tests_runs_status(tests_runs_status, http_error_code)

  if tests_runs_status_id is not None:
    validate_tests_runs_status_id(tests_runs_status_id, http_error_code)

  if table_name is not None:
    validate_table_name(table_name, http_error_code)

  # validate that hostname exisits as 'retiredflag' or equivalent 'hostname_status'
  if hostname is not None and retiredflag is not None:
    validate_hostname(hostname, retiredflag, http_error_code)
  elif hostname is not None and hostname_status is not None:
    retiredflag = to_retiredflag(hostname_status)
    validate_hostname(hostname, retiredflag, http_error_code)

def get_table_fields(table_name):
  validate(table_name=table_name)
  records = execute_sql('DESCRIBE `{}`'.format(table_name))

  table_fields = []
  for data in records:
    table_fields.append(data['Field'])

  return table_fields

def get_table(table_name, hostname=None, retiredflag=None, tests_runs_status_id=None, 
              tests_runs_status=None, tests_name=None, filter=None):
  """Gets table content with optional constraint paramters."""
  validate(table_name=table_name)
  table_names_list = get_table_names_list()
  table = []

  if table_name is 'hostnames':
    table = get_hostnames_table(retiredflag)

  elif table_name is 'tests_runs':
    table = get_tests_runs_table(hostname, tests_runs_status_id, tests_runs_status, tests_name)

  elif table_name is 'tests_runs_queue':
    table = get_tests_runs_queue(hostname)

  elif table_name in table_names_list:
    table = execute_sql('SELECT * FROM `{}`'.format(table_name))
  
  return table

def get_table_names_list():
  table_names_list = execute_sql('SHOW TABLES')
  return table_names_list


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
  """.format(STATUS_QUEUED, HOSTNAME_ACTIVE)

  if hostname is not None:
    # query for queued tests runs on the given hostname
    validate_hostname(hostname, HOSTNAME_ACTIVE)
    sql_command = """
        {} AND hostnames.hostname = '{}'
    """.format(sql_command, hostname)

  tests_runs_queue_table = execute_sql(sql_command)

  return tests_runs_queue_table

def get_tests_runs_table(hostname=None, tests_runs_status_id=None, tests_runs_status=None, 
                         tests_name=None):
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

  if tests_runs_status_id is not None:
    # query only tests with given status id
    validate_tests_runs_status_id(tests_runs_status_id)
    sql_command = """
        {} AND statuses.id = '{}'
    """.format(sql_command, tests_runs_status_id)

  if tests_runs_status is not None:
    # only query tests with given status name
    validate_tests_runs_status(tests_runs_status)
    sql_command = """
        {} AND statuses.name = '{}'
    """.format(sql_command, tests_runs_status)

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
        'test' : data[TESTS_NAME_INDEX],
        'status' : data[STATUSES_INDEX],
        'start_timestamp' : start_timestamp,
        'end_timestamp' : end_timestamp,
        'notes' : data[NOTES_INDEX],
        'config' : data[CONFIG_INDEX],
        'scratch' : data[SCRATCH_INDEX],
        'id' : data[ID_INDEX]
    })

  return tests_runs_table

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

def validate_hostname(hostname, retiredflag=None, http_error_code=404):
  """Validates hostname's existence in the database
  
  Args:
      hostname: string that represents a unique system.
      retiredflag: string that represents a system status.
      http_error_code: status code returned if error is encountered.

  Raises:
      HTTPException: hostname does not exist in the database as statusflag, raise http_error_code 
  """
  hostname_status = 'both {} and {}'.format(HOSTNAME_STATUS_ACTIVE, HOSTNAME_STATUS_RETIRED)
  errors = {}

  sql_command = """
      SELECT hostname FROM hostnames 
      WHERE hostname = '{}' 
  """.format(hostname)
   
  if retiredflag is not None:
    # query hostnames with the retiredflag constraint
    validate_retiredflag(retiredflag)
    hostname_status = to_hostname_status(retiredflag)
    sql_command = """
        {} AND retired = '{}'
    """.format(sql_command, retiredflag)

  records = execute_sql(sql_command)

  if not records:
    # no existing hostname in the database
    error_msg = '\'{}\' Not Found. Queried {} hostnames.'.format(hostname, hostname_status)
    errors.update({'hostname' : error_msg})
  
  if errors:
    abort(http_error_code, message=errors)

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
    error_msg = '\'{}\' Not Found.'.format(hostname_status)
    errors.update({'hostname_status' : error_msg})

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
    error_msg = '\'{}\' Not Found.'.format(retiredflag)
    errors.update({'retiredflag' : error_msg})

  if errors:
    abort(http_error_code, message=errors)

def validate_tests_name(tests_name, http_error_code=404):
  """Validates tests.name existence in the database
  
  Args:
      tests_name: unique stirng identifier of a system test.
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
    error_msg = '\'{}\' Not Found.'.format(tests_name)
    errors.update({'tests_name' : error_msg}) 

  if errors:
    abort(http_error_code, message=errors)

def validate_tests_runs_status(tests_runs_status, http_error_code=404):
  """Validates tests_runs status existence in the database.
  
  Args:
      tests_runs_status: representation of final outcome of a test run.
      http_error_code: status code returned if error is encountered.

  Raises:
      HTTPException: hostname does not exist in the database as statusflag, raise http_error_code 
  """
  errors = {}

  records = execute_sql("""
      SELECT * FROM statuses
      WHERE statuses.name = '{}'
  """.format(tests_runs_status))

  if not records:
    # provided tests runs status does not exist
    error_msg = '\'{}\' Not Found.'.format(tests_runs_status)
    errors.update({'tests_runs_status' : '\'{}\' Not Found.'.format(tests_runs_status)})
    
  if errors:
    abort(http_error_code, message=errors)

def validate_tests_runs_status_by_id(tests_runs_status_id, http_error_code=404):
  """Validates tests_runs_status id existence in the database."""
  errors = {}

  records = execute_sql("""
      SELECT * FROM statuses
      WHERE statuses.id = '{}'
  """.format(tests_runs_status_id))

  if not records:
    # invalid status id provided
    error_msg = '\'{}\' Not Found.'.format(tests_runs_status_id)
    errors.update({'tests_runs_status_id', error_msg}) 

  if errors:
    abort(http_error_code, message=errors)

def validate_table_name(table_name, htpp_error_code=404):
  """Validates that table name exists in database."""
  errors = {}

  records = execute_sql("""
      SHOW TABLES LIKE '{}'
  """.format(table_name))

  if not records:
    # invalid table name
    error_msg = '\'{}\' Not Found.'.format(table_name)
    errors.update({'table_name' : error_msg})

  if errors:
    abort(http_error_code, message=errors)

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
