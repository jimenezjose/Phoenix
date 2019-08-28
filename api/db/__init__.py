# tests_runs status to status_id TODO
# validate tests_runs_status
# single valide function with optional params
# look up by tests_name
# validate arguments from JSON body given 400 error not 404. this is not a db problem rather and route handling prob.
from api.db.utils import (
    get_db,
    close_db)

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
  """Inserts hostname to database.

  Returns:
      Single row entry of new hostname in hostnames table.
  """
  rowid = execute_sql("""
      INSERT INTO hostnames 
      (hostname) VALUES ('{}')
  """.format(hostname), db_commit=True)

  inserted_row = get_hostname_by_id(rowid)
  return inserted_row

def delete_hostname(hostname=None, hostname_id=None):
  """Deletes hostnames by setting hostname.retired to true.

  Returns:
      A list of 'deleted' (newly retired) hostnames.
  """ 
  # to be deleted rows from hostnames table.
  deleted_rows = []

  if hostname is None and hostname_id is None:
    # require at least one parameter 
    return []

  # return list of deleted rows
  if hostname_id is not None:
    deleted_rows = [get_hostname_by_id(hostname_id)]
  elif hostname is not None:
    deleted_rows = get_hostnames(hostname, HOSTNAME_ACTIVE) 

  if deleted_rows:
    # hostname must be active to be deleted.
    row = deleted_rows[0]
    if is_retired(row['retired']):
      return []
  
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

def get_table(table_name, hostname=None, hostname_id=None, hostname_status=None, retiredflag=None, 
              tests_runs_status_id=None, tests_runs_status_name=None, tests_name=None, 
              constraints={}, raw=False):
  """Gets table content with optional constraint paramters.
  
  Args:
    constraints: dictionary with key of table name then values of constraint parameters.
            Example: constraints = {
                                       'tests_runs' : {'id' : 2}
                                   }
    raw: get raw table as represented in the db schema.
  """
  filter = get_database_schema()
  table = []

  # zip contraint params to similar dictionary structure as db schema
  params = zip_params(
    hostname=hostname,
    hostname_id=hostname_id,
    hostname_status=hostname_status,
    retiredflag=retiredflag,
    tests_runs_status_id=tests_runs_status_id,
    tests_runs_status_name=tests_runs_status_name,
    tests_name=tests_name,
  )

  # merge constraints to filter
  for table in constraints:
    for field, value in constraints[table].items():
      if value is not None:
        filter[table].update({field : value})

  # merge param constraints to filter
  for table in params:
    for field, value in params[table].items():
      if value is not None:
        filter[table].update({field : value})

  if table_name is 'tests_runs' and not raw:
    table = get_tests_runs_table(filter)
  elif table_name is 'tests_runs_queue' and not raw:
    table = get_tests_runs_queue(filter)
  else:
    table = get_raw_table(table_name, filter)

  return table

def get_raw_table(table_name, constraints={}):
  """Gets raw filtered data from table_name."""
  table = []

  sql_command = 'SELECT * FROM {}'.format(table_name)
  # filter constraint parameters into query
  authorized_tables = [table_name]
  sql_command = append_sql_constraints(sql_command, constraints, authorized_tables)

  table = execute_sql(sql_command)
  return table

def get_database_schema(table_restrictions=[]):
  """Structured dictionary that reflects the database schema."""
  if not table_restrictions:
    # no table restriction 
    table_restrictions = get_database_table_list()

  schema = {}
  # construct empty skeleton structure of database
  for table_name in get_database_table_list():
    if table_name in table_restrictions:
      table = get_empty_table(table_name)
      schema.update(table)

  return schema

def get_empty_table(table_name):
  """Gets dictionary of table with null key values."""
  empty_table = {table_name : {}}

  for field in get_table_fields(table_name):
    empty_table[table_name].update({field : None})
   
  return empty_table

def get_table_fields(table_name):
  """Gets a list of table field names."""
  records = execute_sql('DESCRIBE `{}`'.format(table_name))

  table_fields = []
  for data in records:
    table_fields.append(data['Field'])

  return table_fields

def get_database_table_list():
  """Gets list of tables existent in database."""
  records = execute_sql('SHOW TABLES', dictionary=False)

  table_names_list = []
  for data in records:
    name = data[0]
    table_names_list.append(name)
  
  return table_names_list

def zip_params(hostname=None, hostname_status=None, retiredflag=None,
              tests_runs_status_id=None, tests_runs_status_name=None, tests_name=None, 
              hostname_id=None):
  """Encapsulates common api paramters to database schema dictionary.
  Example:
     `hostnames` table:
          +----+----------+---------+
          | id | hostname | retired |
          +----+----------+---------+
          | 4  |  sfo-aag |  false  |
          +----+----------+---------+
                    ...

      params passed: 
          hostname='sfo-aad', hostname_status='active'

      example returns: {'hostnames' : {'hostname' : 'sfo-aad', 'retired' : 'false'}}
  """
  if hostname_status:
    # convert to retiredflag and overwrite retiredflag param
    retiredflag = to_retiredflag(hostname_status)

  # empty schema structure of database
  params = get_database_schema(['hostnames', 'tests_runs', 'statuses', 'tests'])

  # populate hostnames table
  params['hostnames'].update({
      'id' : hostname_id,
      'hostname' : hostname,
      'retired' : retiredflag,
  })

  # populate tests_runs table 
  params['tests_runs'].update({
      'hostnames_id': hostname_id,
      'statuses_id' : tests_runs_status_id,
  })

  # populate statuses table
  params['statuses'].update({
      'id' : tests_runs_status_id,
      'name' : tests_runs_status_name
  })

  # populate tests table
  params['tests'].update({
      'name' : tests_name
  })

  # remove null data
  for table in params.keys():
    for field, value in params[table].items():
      if value is None:
        del params[table][field]
    if not params[table]:
      del params[table]

  return params

# TODO CHANGE TESTS_RUNS_STATUS TO TESTS_RUNS_STATUS_NAME
def validate(hostname=None, hostname_status=None, hostname_id=None, retiredflag=None, 
             tests_name=None, tests_runs_status=None, tests_runs_status_id=None, 
             table_name=None, http_error_code=404):
  """Database check of system variable integrity. 
  """ 

  if table_name is not None:
    # check if table exists in database
    validate_table_name(table_name, http_error_code)
  if hostname_status is not None:
    # validate developer defined system variables
    validate_hostname_status(hostname_status, http_error_code)

  # emulate database schema with placing parameters to their respective table locations.
  params = zip_params(
    hostname=hostname,
    hostname_id=hostname_id,
    hostname_status=hostname_status,
    retiredflag=retiredflag,
    tests_runs_status_id=tests_runs_status_id,
    tests_runs_status_name=tests_runs_status,
    tests_name=tests_name,
  )

  # setup prefix notation for all pointers in the database
  database_table_list = get_database_table_list()
  for index in range(len(database_table_list)):
    database_table_list[index] += '_'

  for table in params:
    for field, value in params[table].items():
      validate_field_datatype(table, field, value)
      
      if '_' not in table:
        # field is not a pointer by naming convention 
        return 

      abort(404, message=field)
      for prefix in database_table_list:
        if prefix in table:
          # example: hostnames_id -> ref_table = hostnames, ref_field = id
          ref_table = prefix.replace('_', '')
          ref_field = field.replace(prefix, '')
          validate_field_pointer(ref_table, ref_field, value)

def validate_field_datatype(table, field, value, http_error_code=400):
  """Type checking for enums, integers and strings."""
  datatype = get_field_datatype(table, field)
  error_msg = 'ValueError. Type mismatch for {}: \'{}\''.format(datatype, '{}')
  errors = {}

  if 'int' in datatype:
    try:
      int(value)
      integer = 1
    except ValueError:
      # value is not an integer
      errors.update({table : {field : error_msg.format(value)}})
  elif 'enum' in datatype:
    tuple_str = datatype.replace('enum', '')
    enum = eval(tuple_str)
    if value not in enum:
      # value not in enum list
      errors.update({table : {field : error_msg.format(value)}})
  
  # TODO enum check would be tables tests and statuses since they point to static information

  if errors:
    # throw bad request by default for value error
    abort(http_error_code, message=errors)

def validate_field_pointer(ref_table, ref_field, value, http_errro_code=404):
  """Field points to an invalid row of a table."""
  table_entry = {ref_table : {ref_field : value}}
  records = get_table(ref_table, constraints=table_entry)
  errors = {}

  if not records:
    pointer_field = '{}_{}'.format(ref_table, ref_field)
    errros.update({pointer_field : 'Invalid entry: \'{}\' - Not Found'.format(value)})

  if errors:
    abort(http_error_code, message=errors)

  
def get_field_datatype(table_name, field_name):
  """Fetch datatype of field."""
  table_info = execute_sql('DESCRIBE `{}`'.format(table_name))

  datatype = None
  for row_info in table_info:
    if field_name == row_info['Field']:
      datatype = row_info['Type']

  return datatype

  
    
          




def ___________temp():  
  # input validation
  '''
  table_name, hostname_status, retiredflag, tests_runs_staus_id, tests_runs_status, tests_name
  '''
  if table_name:
    validate_table_name(table_name, http_error_code)

 # validation to check if data exisits in database
  '''
  hostname, hostname_id
  '''

  # zip contraint params to similar dictionary structure as db schema
  params = zip_params(
    hostname=hostname,
    hostname_id=hostname_id,
    hostname_status=hostname_status,
    retiredflag=retiredflag,
    tests_runs_status_id=tests_runs_status_id,
    tests_runs_status_name=tests_runs_status,
    tests_name=tests_name,
  )

  # individual paramter is invalid
  field_error = 'Invalid field name or value \'{}\' not found.'
  # combination of fields were not found together. Example: hostname with given retired flag. 
  combo_error = 'Raw field combination {} with respective raw values {} not found.'

  # iterate through scheme and check if same structure exists in params.
  # edge case would have to handle with clustering table paramters
  # this method of breaking for an incorrect value break when validating for insert? 

  # TODO THIS ASSUMES A DATA EXISTS FOR VALID VALUES IN DATABASE!!!
  for table in params:
    # validate all paramters now structured as fields in tables
    for field, value in params[table].items():
      # validate individual fields
      field_filter = {table : {field : value}}
      table_content = get_table(table, constraints=field_filter)
      if not table_content:
        # no data found on {field : value} in databse
        error_msg = {field : field_error.format(value)}
        abort(http_error_code, message=error_msg)

    # validate combination of fields in the same table
    combo_filter = {table : params[table]}
    valid_combo = get_table(table, constraints=combo_filter)
    if not valid_combo:
      # no row was found in table with combination of fields and values
      field_list = params[table].keys()
      value_list = params[table].values()
      error_msg = {table : combo_error.format(field_list, value_list)}
      abort(http_error_code, message=error_msg)

def get_tests_runs_queue(constraints={}):
  """GET tests_runs_queue with optional constraint parameter - hostname."""
  # query for all tests runs in the queue
  sql_command =  """
      SELECT hostnames.hostname 
      FROM hostnames, tests_runs, tests_runs_queue
      WHERE hostnames.id = tests_runs.hostnames_id
      AND tests_runs.id = tests_runs_queue.test_runs_id
      AND tests_runs.statuses_id = '{}'
      AND hostnames.retired = '{}'
  """.format(STATUS_QUEUED, HOSTNAME_ACTIVE)

  # restrict query on constraints
  authorized_tables = ['hostnames', 'tests_runs', 'tests_runs_queue']
  sql_command = append_sql_constraints(sql_command, constraints, authorized_tables)

  tests_runs_queue = execute_sql(sql_command)

  return tests_runs_queue

# empty authorized is all tables or no tables to be autghorized? TODO
def append_sql_constraints(sql_command, constraints={}, authorized_tables=[]):
  """appends sql conditions according to the constraints paramter.

  Args:
      sql_command: mysql command string that *must* contain the WHERE clause.
  """

  if ' WHERE ' not in sql_command:
    # append dummy where clause
    sql_command = '{} WHERE TRUE'.format(sql_command)

  for table in constraints:
    if table not in authorized_tables:
      continue
    for field, value in constraints[table].items():
      if field in get_table_fields(table) and value is not None:
        sql_command = """
            {} AND {}.{} = '{}'
        """.format(sql_command, table, field, value)

  return sql_command

def get_tests_runs_table(constraints={}):
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
      AND statuses.id = tests_runs.statuses_id
  """

  # append filter conditions
  authorized_tables = ['hostnames', 'tests', 'tests_runs', 'statuses']
  sql_command = append_sql_constraints(sql_command, constraints, authorized_tables)

  # get raw data (reason: key naming collision with tests.name and statuses.name)
  records = execute_sql(sql_command, dictionary=False)

  if not records:
    # no running tests
    return []

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

# TODO NO NEED FOR THIS FUNCTION IT IS THE SAME AS GET TABLE WITH GIVEN FILTER PARAMTERS
def get_hostnames(hostname, retiredflag=None, hostname_status=None):
  """Gets hostname rows by hostname and with an optional retired status constraint."""
  # query for hostname
  hostnames = get_table(
      'hostnames',
      hostname=hostname,
      retiredflag=retiredflag,
      hostname_status=hostname_status
  )
  return hostnames

def get_hostname_by_id(hostname_id):
  """Gets hostnames row by row id in hostnames table."""
  hostname_row_list = get_table('hostnames', hostname_id=hostname_id)

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

