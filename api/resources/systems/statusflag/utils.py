from api.db import (
    HOSTNAME_RETIRED,
    HOSTNAME_ACTIVE) 

from flask_restful import abort

SYSTEM_STATUS_ACTIVE = 'active'
SYSTEM_STATUS_RETIRED = 'retired'

def validate_systems_statusflag(statusflag, http_error_code=404):
  """Validates statusflag is 'active' or 'retired'.
  
  Args:
      statusflag: string that represents a system status.
      http_error_code: status code returned if error is encountered.

  Raises:
      HTTPException: System statusflag is not valid, raises http_error_code.
  """
  errors = {}

  if not is_active(statusflag) and not is_retired(statusflag):
    errors.update({'statusflag' : 'Provided flag \'{}\' is not valid.'.format(statusflag)})

  if errors:
    abort(http_error_code, message=errors)

def is_active(statusflag):
  return statusflag == SYSTEM_STATUS_ACTIVE

def is_retired(statusflag):
  return statusflag == SYSTEM_STATUS_RETIRED

def to_retiredflag(statusflag):
  """Converts a statusflag to a retiredflag as indicated from the database."""
  if is_retired(statusflag):
    return HOSTNAME_RETIRED

  return HOSTNAME_ACTIVE
