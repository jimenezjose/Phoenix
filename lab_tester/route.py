from flask import Blueprint
from flask_restful import Api

# Resources
#from .resources.Hello import Hello 
#from .resources import Testruns
from .resources.testruns import Testruns

api_bp = Blueprint('api', __name__)
api = Api(api_bp)

# Route
#api.add_resource(Hello, '/Hello')
Testruns.add_all_resources(api, '/testruns')
