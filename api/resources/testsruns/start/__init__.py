from api.db import (
    execute_sql,
    HOSTNAME_ACTIVE,
    STATUS_RUNNING, 
    STATUS_SCHEDULED, 
    STATUS_STARTED,
    NULL_TIMESTAMP,
    validate_hostname,
    validate_tests_name,
    get_tests_runs_queue) 

from flask_restful import Resource, reqparse

class Start(Resource):
  """testruns/start resource to begin a new testrun."""

  def post(self):
    """POST request to begin testrun on active 'hostname' with 'test'."""
    parser = reqparse.RequestParser()

    # require 'hostname' and 'test_id' parameter from request. 
    parser.add_argument('hostname', type=str, required=True) 
    parser.add_argument('tests_name', type=str, required=True)
    args = parser.parse_args()
    
    # validate active hostname and test name
    validate_hostname(args['hostname'], HOSTNAME_ACTIVE)
    validate_tests_name(args['tests_name'])

    # query for currently running tests on the given hostname
    running_tests = get_tests_runs_table(args['hostname'], STATUS_RUNNING)
    # query for queued tests in line to occupy hostname
    tests_queue = get_tests_runs_queue(args['hostname'])

    # register status of tests run
    args['status'] = STATUS_SCHEDULED
    if not running_tests and not tests_queue:
      # hostname server ready to directly host a test_run
      args['status'] = STATUS_STARTED 

    # get hostnames_id and tests_id of hostname
    records = execute_sql("""
        SELECT hostnames.id, tests.id
        FROM hostnames, tests
        WHERE hostnames.retired = '{}'
        AND hostnames.hostname = '{}'
        AND tests.name = '{}'
    """.format(HOSTNAME_ACTIVE, args['hostname'], args['tests_name']))

    # register hostname and test id to args dictionary
    args['hostnames_id'] = records[0][0]
    args['tests_id'] = records[0][1]
  
    # inserts into tests_runs 
    db_lastrowid = execute_sql("""
        INSERT INTO tests_runs
        (hostnames_id, tests_id, status) VALUES ('{}', '{}', '{}')
    """.format(args['hostname_id'], args['tests_id'], args['status']), db_commit=True)
    
    # register testrun_id of new inserted test_run row
    args['test_runs_id'] = db_lastrowid

    if args['status'] == STATUS_SCHEDULED:
      # insert test_run id to the queue
      execute_sql("""
          INSERT INTO tests_runs_queue
          (tests_id, test_runs_id) VALUES (%s, %s)
      """.format(args['tests_id'], args['test_runs_id']), db_commit=True)
 
    return {'message' : '{}'.format(args)}, 201

  @staticmethod
  def add_all_resources(api, path):
    api.add_resource(Start, path)
