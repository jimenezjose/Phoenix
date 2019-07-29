from api.db import (
    get_db, 
    STATUS_RUNNING, 
    STATUS_SCHEDULED, 
    STATUS_STARTED,
    NULL_TIMESTAMP) 

from flask_restful import Resource, reqparse

class Start(Resource):
  """testruns/start resource to begin a new testrun."""

  def post(self):
    """POST request to begin testrun on 'hostname' with 'test'."""
    db = get_db()
    cursor = db.cursor()
    parser = reqparse.RequestParser()

    # require 'hostname' and 'test_id' parameter from request. 
    parser.add_argument('hostname', type=str, required=True) 
    parser.add_argument('test', type=str, required=True)
    args = parser.parse_args()
    
    # validate unretired hostname and test
    sql_query = """
        SELECT hostnames.id, tests.id
        FROM hostnames, tests
        WHERE hostnames.retired = '0'
        AND hostnames.hostname = %s 
        AND tests.name = %s
    """
    values = (args['hostname'], args['test']) 
    cursor.execute(sql_query, values)
    records = cursor.fetchall()

    if not records:
      # invalid argument supplied
      hostname = args['hostname']
      test = args['test']
      return {'message' : 'hostname: {} or test: {} Not Found.'.format(hostname, test)}, 404

    # register validated hostname and test id to args dictionary
    args['hostnames_id'] = records[0][0]
    args['tests_id'] = records[0][1]

    # query for currently running tests on the given hostname
    sql_query = """
        SELECT hostnames.hostname 
        FROM hostnames, tests_runs
        WHERE hostnames.hostname = %s
        AND hostnames.id = tests_runs.hostnames_id
        AND tests_runs.end_timestamp = %s
        AND tests_runs.status = %s
    """
    values = (args['hostname'], NULL_TIMESTAMP, STATUS_RUNNING)
    cursor.execute(sql_query, values)
    running_tests = cursor.fetchall()
    
    # query for queued tests in line to occupy hostname
    sql_query = """
        SELECT hostnames.hostname 
        FROM hostnames, tests_runs, tests_runs_queue
        WHERE hostnames.hostname = %s
        AND hostnames.id = tests_runs.hostnames_id
        AND tests_runs.id = tests_runs_queue.test_runs_id
    """
    values = (args['hostname'],)
    cursor.execute(sql_query, values)
    queued_tests = cursor.fetchall()

    args['status'] = STATUS_SCHEDULED
    if not running_tests and not queued_tests:
      # hostname server ready to directly host a test_run
      args['status'] = STATUS_STARTED 
  
    # inserts into tests_runs 
    sql_insert = """
        INSERT INTO tests_runs
        (hostnames_id, tests_id, status) VALUES (%s, %s, %s)
    """
    values = (args['hostnames_id'], args['tests_id'], args['status'])
    cursor.execute(sql_insert, values)
    db.commit() 
    
    # register testrun_id of new inserted test_run row
    args['test_runs_id'] = cursor.lastrowid

    if args['status'] == STATUS_SCHEDULED:
      # insert test_run id to the queue
      sql_insert = """
          INSERT INTO tests_runs_queue
          (tests_id, test_runs_id) VALUES (%s, %s)
      """
      values = (args['tests_id'], args['test_runs_id'])
      cursor.execute(sql_insert, values)
      db.commit()
 
    return {'message' : '(hostname, tests_id) : {}'.format(args)}, 201

def add_all_resources(api, path):
  api.add_resource(Start, path)
