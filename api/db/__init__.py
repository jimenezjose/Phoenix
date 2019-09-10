# validate tests_runs_status
# single valide function with optional params
# look up by tests_name
# validate arguments from JSON body given 400 error not 404. this is not a db problem rather and route handling prob.
# TODO Depricate get hostname by id and use get data by id
from api.db.utils import *
from flask_restful import abort

# TODO remove dependency
def validate_hostname(hostname=None):
  return
def validate_tests_name(tests=None):
  return

def get_data_by_id(table_name, table_id):
  data = execute_sql("""
      SELECT * FROM `{0}` 
      WHERE {0}.id = '{1}'
  """.format(table_name, table_id)) 

  if not data:
    return None
  
  return data[0]

def insert_tests_run(hostname, tests_name, statuses_id):
  """Insert a new tests run to the database."""
  hostnames_data = get_table('hostnames', hostname=hostname, retiredflag=HOSTNAME_ACTIVE)
  tests_data = get_table('tests', tests_name=tests_name)

  errors = {}
  if not hostnames_data:
    error_msg = 'hostname \'{}\' Not Found.'.format(hostname)
    errors.update({'hostnames' : error_msg})
  elif not tests_data:
    error_msg = 'test \'{}\' Not Found.'.format(tests_name)
    errors.update({'tests' : error_msg})
  if errors:
    # intrnal server error - invalid hostname or testsname
    abort(500, message=errors)

  # active hostname and tests name is guaranteed to be unique
  hostnames_id = hostnames_data[0]['id']
  tests_id = tests_data[0]['id']

  rowid = execute_sql("""
      INSERT INTO tests_runs
      (hostnames_id, tests_id, statuses_id) VALUES('{}', '{}', '{}')
  """.format(hostnames_id, tests_id, statuses_id), db_commit=True)
  
  inserted_row = get_data_by_id('tests_runs', rowid)
  
  return inserted_row


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

def delete_hostname(hostname=None, hostnames_id=None):
  """Deletes hostnames by setting hostname.retired to true.

  Returns:
      A list of 'deleted' (newly retired) hostnames.
  """ 
  # to be deleted rows from hostnames table.
  deleted_rows = []

  if hostname is None and hostnames_id is None:
    # require at least one parameter 
    return []

  # return list of deleted rows
  if hostnames_id is not None:
    deleted_rows = [get_hostname_by_id(hostnames_id)]
  elif hostname is not None:
    deleted_rows = get_hostnames(hostname, HOSTNAME_ACTIVE) 

  if deleted_rows:
    # hostname must be active to be deleted.
    row = deleted_rows[0]
    if is_retired(row['retired']):
      return []
  else:
    # nothing to delete
    return []
  
  sql_command = """
      UPDATE hostnames
      SET retired = '{}'
      WHERE retired = '{}'
  """.format(HOSTNAME_RETIRED, HOSTNAME_ACTIVE)

  if hostnames_id is not None:
    # delete hostname row by id
    sql_command = """
        {} AND id = '{}'
    """.format(sql_command, hostnames_id)
  elif hostname is not None:
    # delete hostname by name
    sql_command = """
      {} AND hostname = '{}'
    """.format(sql_command, hostname)

  execute_sql(sql_command, db_commit=True)

  return deleted_rows




def add_filter_query_parameters(parser, table_name):
  """Adds filtering query paramters based from table name.

  Args:
      parser: reqparse object from RequestParser
      table_name: name of table interested to be filtered.
  """
  authorized_tables = get_linked_tables(table_name)
  filter = get_database_schema(authorized_tables)
  duplicate_fields = get_duplicate_field_names(authorized_tables)

  # add query parameters 
  for table in filter:
    for field in filter[table]:
      if field in duplicate_fields:
        # clarify field by prepending unique table name
        field = '{}_{}'.format(table, field)
      parser.add_argument(field, type=str, location='args')

def parse_filter_query_parameters(args, table_name):
  """Parse query parameters from args and set up paramters in their database layout.

  Args: 
      args: parsed query string from reqparse parser function parse_args() 
      table_name: name of table in interest to be filtered with query params.

  Example:
      args = {'hostnames_id' : 1, 'tests_name' : 'bios_up_down'}
      Returns:
          {
            {'hostnames' : {'id' : 1}}
            {'tests' : {'name' : 'bios_up_down'}}
          }

  Raises:
      HTTPException: InternalServerError
          HTTP status code : 500
          * Invalid supplied 'args' supplied to function call.

  Returns:
      Dictionary of database constraints based from query parameters. Readily to be used as the 
      constraints paramters to get_table().
  """
  authorized_tables = get_linked_tables(table_name)
  constraints = get_database_schema(authorized_tables)
  duplicate_fields = get_duplicate_field_names(authorized_tables)

  # populate constriants with query parameters
  for table in constraints:
    for field in constraints[table]:
      index = field
      if field in duplicate_fields:
        # clarify unique field index in args
        index = '{}_{}'.format(table, field)
      if index not in args:
        # undefined index for incorrectly formatted args
        abort(500, message={table_name: 'Error. Query paramters cannot be parsed.'})
      value = args[index]
      constraints[table].update({field : value})

  return constraints

def get_table(table_name, hostname=None, hostnames_id=None, hostname_status=None, retiredflag=None, 
              statuses_id=None, statuses_name=None, tests_name=None, 
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
    hostnames_id=hostnames_id,
    hostname_status=hostname_status,
    retiredflag=retiredflag,
    statuses_id=statuses_id,
    statuses_name=statuses_name,
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

  if raw:
    table = get_raw_table(table_name, filter)
  else:
    table = get_detailed_table(table_name, filter)

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
    table_restrictions = get_database_tables()

  schema = {}
  # construct empty skeleton structure of database
  for table_name in get_database_tables():
    if table_name in table_restrictions:
      table = get_empty_table(table_name)
      schema.update(table)

  return schema

def get_empty_table(table_name, raw=False):
  """Gets empty dictionary schema of table name."""
  empty_table = []

  # TODO
  raw = True

  if raw:
    empty_table = _get_empty_raw_table(table_name)
  else:
    empty_table = _get_empty_detailed_table(table_name)

  return empty_table

def _get_empty_raw_table(table_name):
  """Gets dictionary of table with null key values."""
  empty_table = {table_name : {}}

  for field in get_table_fields(table_name):
    empty_table[table_name].update({field : None})
   
  return empty_table

def _get_empty_detailed_table(table_name):
  return []

def get_table_fields(table_name):
  """Gets a list of table field names."""
  records = execute_sql('DESCRIBE `{}`'.format(table_name))

  table_fields = []
  for data in records:
    table_fields.append(data['Field'])

  return table_fields

def get_database_tables():
  """Gets list of tables existent in database."""
  records = execute_sql('SHOW TABLES', dictionary=False)

  table_names_list = []
  for data in records:
    name = data[0]
    table_names_list.append(name)
  
  return table_names_list

def zip_params(hostname=None, hostname_status=None, retiredflag=None,
              statuses_id=None, statuses_name=None, tests_name=None, 
              hostnames_id=None):
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
      'id' : hostnames_id,
      'hostname' : hostname,
      'retired' : retiredflag,
  })

  # populate tests_runs table 
  params['tests_runs'].update({
      'hostnames_id': hostnames_id,
      'statuses_id' : statuses_id,
  })

  # populate statuses table
  params['statuses'].update({
      'id' : statuses_id,
      'name' : statuses_name
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

def validate(hostname=None, hostname_status=None, hostnames_id=None, retiredflag=None, 
             tests_name=None, statuses_name=None, statuses_id=None, 
             table_name=None, http_error_code=404):
  """Database check of system variable integrity."""
  if table_name is not None:
    # check if table exists in database
    validate_table_name(table_name, http_error_code)
  if hostname_status is not None:
    # validate developer defined system variables
    validate_hostname_status(hostname_status, http_error_code)

  # emulate database schema with placing parameters to their respective table locations.
  params = zip_params(
    hostname=hostname,
    hostnames_id=hostnames_id,
    hostname_status=hostname_status,
    retiredflag=retiredflag,
    statuses_id=statuses_id,
    statuses_name=statuses_name,
    tests_name=tests_name,
  )

  for table in params:
    for field, value in params[table].items():
      validate_field_datatype(table, field, value)
     
      if field == 'id':
        # validate that 'id' points to a defined table row
        validate_field_pointer(table, field, value)
        continue
      elif '_' not in field:
        # field is not a pointer by naming convention 
        continue

      pointer_data = parse_field_pointer(field)
      if pointer_data is not None:
        # example: field=hostnames_id -> ref_table='hostnames', ref_field='id'
        ref_table = pointer_data[0]
        ref_field = pointer_data[1]
        validate_field_pointer(ref_table, ref_field, value)

def validate_field_datatype(table, field, value, http_error_code=400):
  """Type checking for enums, integers and strings."""
  table_entry = {table : {field :  value}}
  datatype = get_field_datatype(table, field)

  invalid_entry_msg = 'Invalid Entry. {}.{} with value \'{}\' Not Found'.format(table, field, '{}')
  value_error_msg = 'ValueError. Type mismatch for {}: \'{}\''.format(datatype, '{}')
  errors = {}

  if 'int' in datatype:
    try:
      int(value)
      integer = 1
    except ValueError:
      # value is not an integer
      errors.update({table : {field : value_error_msg.format(value)}})
  elif 'enum' in datatype:
    tuple_str = datatype.replace('enum', '')
    enum = eval(tuple_str)
    if value not in enum:
      # value not in enum list
      errors.update({table : {field : value_error_msg.format(value)}})
  elif table in DATATYPE_TABLES: 
    # value is restricted based on the dynamic data in a table.
    valid_entry = get_table(table, constraints=table_entry) 
    if not valid_entry:
      # no data matched the value provided in the given table
      errors.update({table : {field : invalid_entry_msg.format(value)}})

  if errors:
    # throw bad request by default for value error
    abort(http_error_code, message=errors)

def validate_field_pointer(ref_table, ref_field, value, http_error_code=404):
  """Field points to an invalid row of a table."""
  table_entry = {ref_table : {ref_field : value}}
  pointer_data = get_table(ref_table, constraints=table_entry)

  error_msg = 'Invalid entry. {}.{} with value \'{}\' Not Found'.format(ref_table, ref_field, '{}')
  errors = {}

  if not pointer_data:
    pointer_field = '{}_{}'.format(ref_table, ref_field)
    errors.update({pointer_field : error_msg.format(value)})

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

def get_tests_runs_queue(constraints={}):
  """GET tests_runs_queue with optional constraint parameter - hostname."""
  # TODO DEPRICATED
  return ['depricated']
  # query for all tests runs in the queue

  # restrict query on constraints
  authorized_tables = ['hostnames', 'tests_runs', 'tests_runs_queue']
  sql_command = append_sql_constraints(sql_command, constraints, authorized_tables)

  tests_runs_queue = execute_sql(sql_command)

  return tests_runs_queue

# empty authorized is all tables or no tables to be autghorized? TODO
def append_sql_constraints(sql_command, constraints={}, authorized_tables=[]):
  """appends sql conditions according to the constraints paramter.

  Args:
      sql_command: mysql command string that should contain the WHERE clause.
  """
  if 'WHERE' not in sql_command:
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

def get_duplicate_field_names(table_list):
  """Gets a list of duplicate field names found across table_list.

  Args:
      table_list: list of table names.

  Returns:
      List of dupicate field names found.
  """
  duplicate_fields = set()
  unique_fields = set()

  for table in table_list:
    for field in get_table_fields(table):
      if field in unique_fields:
        # duplicate field found
        duplicate_fields.add(field)
      else:
        unique_fields.add(field)

  return list(duplicate_fields)

def parse_field_pointer(field_name):
  """Parses a field pointer into describing the table and field it points to.

  Returns:
      A tuple of referenced table and field resepectively if the field is 
      a pointer. Otherwise None will be returned.
  """
  prefix_tables = ['{}_'.format(table) for table in get_database_tables()]
  # sort prefix table in descending string length to avoid ambiguous parse for case 'tests_runs_id'
  prefix_tables.sort(key=len, reverse=True)
  
  if '_' not in field_name:
    # field is not a pointer by naming convention
    return None

  for prefix in prefix_tables:
    if prefix in field_name:
      ref_table = prefix[:-1]
      ref_field = field_name.replace(prefix, '')
      return (ref_table, ref_field)

  return None

def get_linked_tables(table_name):
  """Gets all tables assosiated with the fields in table_name."""
  prefix_tables = ['{}_'.format(table) for table in get_database_tables()]
  linked_tables = set([table_name])

  for field in get_table_fields(table_name):
    pointer_data = parse_field_pointer(field)
    if pointer_data is not None:
      # recurse to fetch interlinked tables
      table = pointer_data[0]
      interlinked_tables = get_linked_tables(table)
      linked_tables |= set(interlinked_tables)

  return list(linked_tables)

def get_detailed_table(table_name, constraints={}):
  authorized_tables = get_linked_tables(table_name)
  duplicate_fields = get_duplicate_field_names(authorized_tables)

  field_list = []
  condition_list = []
  for table in authorized_tables:
    for field in get_table_fields(table):
      # query for all fields associated with the authorized tables

      # build aliases for duplicate field names - avoids dictionary key collision from mysql query
      field_identifier = '{}.{}'.format(table, field)
      if field in duplicate_fields:
        # prepend string differentiater using the field's unique table name
        unique_alias = '{}_{}'.format(table, field)
        field_identifier = '{} AS {}'.format(field_identifier, unique_alias)
      field_list.append(field_identifier)

      # build join conditions for combining relational table information.
      pointer_data = parse_field_pointer(field)
      if pointer_data is not None:
        # field is referencing data on different table
        ref_table = pointer_data[0]
        ref_field = pointer_data[1]
        condition = '{}.{} = {}.{}'.format(table, field, ref_table, ref_field)
        condition_list.append(condition)
        
  # build select statment that specifies table fields to query
  delimiter = ', '
  union = ' AND ' 
  select_fields = delimiter.join(field_list)
  from_tables = delimiter.join(authorized_tables)  
  join_conditions = union.join(condition_list) if condition_list else 'TRUE'

  sql_command = """
      SELECT {}
      FROM {}
      WHERE {}
  """.format(select_fields, from_tables, join_conditions)

  # add filtering constraints to query
  sql_command = append_sql_constraints(sql_command, constraints, authorized_tables)
  tests_runs_table = execute_sql(sql_command)
  return tests_runs_table

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

def get_hostname_by_id(hostnames_id):
  """Gets hostnames row by row id in hostnames table."""
  hostname_row_list = get_table('hostnames', hostnames_id=hostnames_id)

  # there is only one hostname with the given unique id
  hostname_row = None
  if hostname_row_list:
    # valid id passed
    hostname_row = hostname_row_list[0]

  return hostname_row

def get_running_tests(hostname=None, hostnames_id=None, constraints={}):
  """Gets all tests_runs for a hostname that are currently running or queued."""
  filter = get_empty_table('tests_runs')

  if constraints:
    filter.update(constraints)

  if hostnames_id is not None:
    filter.update(zip_params(hostnames_id=hostnames_id))
  elif hostname is not None:
    filter.update(zip_params(hostname=hostname))

  # running tests have an undefined end time
  filter['tests_runs'].update({
      'end_timestamp' : NULL_TIMESTAMP
  })

  running_tests = get_table('tests_runs', constraints=filter)

  return running_tests

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

