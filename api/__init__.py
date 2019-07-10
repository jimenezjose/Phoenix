from flask import Flask, g
import os

def create_app(test_config=None):
        # create and configure the app
        app = Flask(__name__, instance_relative_config=True)

        app.config.from_mapping(
                SECRET_KEY='dev',
                DATABASE=os.path.join(app.instance_path, 'lab-tester-api.mysql'),
        )

        if test_config is None:
                # load the instance config, if it exists, when not testing
                app.config.from_pyfile('config.py', silent=True)
        else:
                # load the test config if passed in
                app.config.from_mapping(test_config)

	# ensure the instance folder exists
        try:
                os.makedirs(app.instance_path)
        except OSError:
                pass

        # welcoming page
        @app.route('/')
        def index():
	        return 'Phoenix Time'

	# set up url architecture /api/...
        from api import route
        app.register_blueprint(route.api_bp, url_prefix='/api')

	# set up database
        from api import db
        db.init_app(app)

        return app
