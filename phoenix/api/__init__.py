from api import route
from api import db

from flask import Flask

def create_app():
  """Creates a factory design Flask Application.

  Creates a Flask Instance, connects the app to 
  the database, and sets up the url architecture.

  Returns:
      A flask application with a registered blueprint 
      for url architecture build up and database connection.
  """

  # create and configure the app
  app = Flask(__name__, instance_relative_config=True)

  @app.route('/')
  def index():
    """Welcoming Page."""
    return 'Phoenix Time'

  # set up url architecture /api/...
  app.register_blueprint(route.api_bp, url_prefix='/api')

  # set up database
  db.init_app(app)

  return app
