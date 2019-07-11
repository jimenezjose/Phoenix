# local resources
from .hostname import Hostname

from flask_restful import Resource, reqparse
from api.db import get_db

def add_all_resources(api, path):
  api.add_resource(Systems, path)
  # recursively add all sub-resources
  Systems.add_all_resources(api, path)

''' /systems '''
class Systems(Resource):
  def get(self):
    ''' get all unretired hostnames '''
    db = get_db()
    cursor = db.cursor()
    sql_query="SELECT hostname FROM hostnames WHERE retired = '0'"
    cursor.execute(sql_query)
    records = cursor.fetchall()
    return {"list of unretired hostnames" : str(records)}

  def post(self):
    ''' adds hostname to db '''
    # require 'hostname' parameter from request
    parser = reqparse.RequestParser()
    parser.add_argument('hostname', required=True) 
    args = parser.parse_args()

    # insert hostname into db
    db = get_db()
    cursor = db.cursor()
    sql_insert="INSERT INTO hostnames (hostname) VALUES (%s)"
    values=(args['hostname'],)
    cursor.execute(sql_insert, values)
    db.commit()

    return {"inserted" : str(args['hostname'])}


  @staticmethod
  def add_all_resources(api, path):
    Hostname.add_all_resources(api, path + '/<string:hostname>')

