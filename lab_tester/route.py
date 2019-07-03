from flask import Blueprint
from flask_restful import Api

# Resources
from resources.Hello import Hello


bp = Blueprint('api', __name__)
api = Api(bp)

# Route
api.add_resource(Hello, '/Hello')
