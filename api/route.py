# Resources
from .resources.systems import Systems
from .resources.tests import Tests
from .resources.testruns import Testruns

from flask import Blueprint
from flask_restful import Api

api_bp = Blueprint('api', __name__)
api = Api(api_bp)

# Route
Systems.add_all_resources(api, '/systems')
Tests.add_all_resources(api, '/tests')
Testruns.add_all_resources(api, '/testruns')
