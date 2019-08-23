import mysql.connector
from flask import g
from flask_restful import abort

def get_db():
  """Getter method to retrieve the current database connection.
    
  Returns:
      A mysql database connection corresponding with host, database, 
      and port as configured below.
  """
  if 'db' not in g:
    g.db = mysql.connector.connect(
        host = 'localhost',
        user = 'root',
        passwd = 'Jose88',
        database = 'TestPhoenix',
        port = 3306
    )
  return g.db

def close_db(error):
  """Closes the database connection."""
  db = g.pop('db', None)

  if db is not None:
    db.close()
