from api.db import (
    STATUS_QUEUED,
    STATUS_STARTED,
    HOSTNAME_ACTIVE,
    get_running_tests,
    get_table,
    insert_tests_run,
    insert_tests_runs_queue,
    validate)

from flask_restful import abort, Resource, reqparse

class Start(Resource):
  """testruns/start resource to begin a new testrun."""

  def post(self):
    """POST request to begin testrun on active 'hostname' with 'test'.

    Returns:
        Success:
            Status Code: 201 Created
                * inserted tests_runs dictionary row
        Failure:
            Status Code: 409 Conflict
                * hostname or test name supplied not found.
                * attempt to run a test on a retired hostname.
    """
    parser = reqparse.RequestParser()

    parser.add_argument('hostname', type=str, required=True)
    parser.add_argument('tests_name', type=str, required=True)
    args = parser.parse_args()

    # validate that hostname and tests name exist in the db
    validate(
        hostname=args['hostname'], 
        tests_name=args['tests_name'],
        http_error_code=409
    )

    # validate active hostname
    active_hostname = get_table(
        'hostnames',
        hostname=args['hostname'],
        retiredflag=HOSTNAME_ACTIVE
    )
    if not active_hostname:
      # throw 409 Conflict error for attempt to run a test on a retired system
      error_msg = 'System \'{}\' must be active.'.format(args['hostname'])
      abort(409, message={'hostname' : error_msg})

    # if hostname has no running tests, directly execute test on hostname else queue test
    running_tests = get_running_tests(hostname=args['hostname'])
    # assume hostname is busy and queue test
    statuses_id = STATUS_QUEUED
    if not running_tests:
      # hostname server ready to directly host a test_run
      statuses_id = STATUS_STARTED

    inserted_tests_run = insert_tests_run(
        hostname=args['hostname'], 
        tests_name=args['tests_name'], 
        statuses_id=statuses_id
    )

    if statuses_id == STATUS_QUEUED:
      # insert to queue
      insert_tests_runs_queue(inserted_tests_run['id'])

    return inserted_tests_run, 201

  @staticmethod
  def add_all_resources(api, path):
    api.add_resource(Start, path)
