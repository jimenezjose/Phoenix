import os

from api import route
from api import db

from flask import Flask, g

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__, instance_relative_config=True)

  # welcoming page
  @app.route('/')
  def index():
    return 'Phoenix Time'

  # set up url architecture /api/...
  app.register_blueprint(route.api_bp, url_prefix='/api')

  # set up database
  db.init_app(app)

  return app
