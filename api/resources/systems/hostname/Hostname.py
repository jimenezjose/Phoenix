from flask_restful import Resource
from api.db import get_db
# local resources
from .test import Test

def add_all_resources(api, path):
	api.add_resource(Hostname, path)
	# recursively add all sub-resources
	Hostname.add_all_resources(api, path)

''' systems/<string:hostname> '''
class Hostname(Resource):
	def get(self, hostname):
		''' Get info about unretired system '''
		db = get_db()
		cursor = db.cursor()
		sql_query = "SELECT id FROM hostnames WHERE hostname = %s"
		values = (hostname,)
		cursor.execute(sql_query, values)
		records = cursor.fetchall()
		return {"message" : "Get info about unretired system " + hostname + " with id: " + str(records[0])}

	def delete(self, hostname):
		''' update the state of the hostname to retired '''
		# TODO might be an edge case: multiple hostnames with the same name with distinct ids.
		db = get_db()
		cursor = db.cursor()
		sql_update = "UPDATE hostnames SET retired = '1' WHERE hostname = %s"
		values = (hostname,)
		cursor.execute(sql_update, values)
		db.commit()
		return {"message" : "DELETE: Set " + hostname + " as retired with id: TODO"}

	@staticmethod
	def add_all_resources(api, path):
		# recursively add sub-packaged resources
		Test.add_all_resources(api, path + '/test')
