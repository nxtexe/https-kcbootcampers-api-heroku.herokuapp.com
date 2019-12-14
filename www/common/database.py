import pymongo
import urllib

class Database():
	#mongodb+srv://nxtexe:d4rkw%40tch3r@cluster0-ln3eh.mongodb.net/test?retryWrites=true&w=majority
	URI = "mongodb+srv://nxtexe:"+urllib.parse.quote("d4rkw@tch3r")+"@cluster0-ln3eh.mongodb.net/test?retryWrites=true&w=majority"
	DATABASE = None

	@staticmethod
	def initialize():
		client = pymongo.MongoClient(Database.URI)
		Database.DATABASE = client['dynamic']

	@staticmethod
	def insert(collection, data):
		Database.DATABASE[collection].insert(data)

	@staticmethod
	def find(collection, query):
		return Database.DATABASE[collection].find(query)

	@staticmethod
	def search(collection, qs):
		query = {"$text": {"$search": qs }} 
		return Database.DATABASE[collection].find(query)

	@staticmethod
	def find_one(collection, query):
		return Database.DATABASE[collection].find_one(query)


	@staticmethod
	def remove(collection, data):
		Database.DATABASE[collection].remove(data)


	@staticmethod
	def update(collection, query, new_val):
		"""query={"email": email}, new_val={"$set": {"password": password}} """
		Database.DATABASE[collection].update_one(query, new_val)
