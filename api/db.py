import mysql.connector

import click
from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
        if 'db' not in g:
                g.db = mysql.connector.connect(
                        host="localhost",
                        user="root",
                        passwd="Jose88",
                        database="TestPhoenix",
			port=3306
                )
        return g.db     

def close_db(error):
	db = g.pop('db', None)

	if db is not None:
		db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('scheme.sql') as f:
        db.executescript(f.read().decode('utf8'))

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
	app.teardown_appcontext(close_db)
	app.cli.add_command(init_db_command)
