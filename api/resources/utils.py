from api.db import (
    execute_sql,
    HOSTNAME_RETIRED,
    HOSTNAME_ACTIVE) 

from flask_restful import abort

HOSTNAME_STATUS_ACTIVE = 'active'
HOSTNAME_STATUS_RETIRED = 'retired'

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
  errors = {}

  records = execute_sql("""
      SELECT hostname FROM hostnames 
      WHERE hostname = '{}' AND retired = '{}'
   """.format(hostname, retiredflag))

  if not records:
    # no existing hostname in database
    errors.update({'hostname' : '{} hostname \'{}\' Not Found.'.format(statusflag, hostname)})
  
  if errors:
    abort(http_error_code, message=errors)

def validate_tests_name(tests_name):
  errors = {}

  records = execute_sql("""
      SELECT * FROM tests 
      WHERE tests.name = '{}'
  """.format(tests_name))

def is_retired(retiredflag):
  return retiredflag == HOSTNAME_RETIRED

def is_active(retiredflag):
  return retiredflag == HOSTNAME_ACTIVE

def to_hostname_status(retiredflag):
  """Converts retiredflag to a hostname status strings {'active', 'retired'}"""
  if is_retired(retiredflag):
    return HOSTNAME_STATUS_RETIRED

  return HOSTNAME_STATUS_ACTIVE
