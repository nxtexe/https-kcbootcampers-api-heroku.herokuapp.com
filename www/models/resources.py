from common.database import Database
import uuid


class Book():
	def __init__(self, name, href, _id=None):
		self.name = name
		self.href = href
		self._id = uuid.uuid4().hex if _id is None else _id


	@classmethod
	def search(cls, qs):
		books = Database.search(collection="books", qs=qs)
		return [cls(**book) for book in books]


	@staticmethod
	def remove_fr_mongo(book_id):
		Database.remove(collection="books", data={"_id": book_id})


	def update(self, key, value):
		Database.update(collection="books", query={"_id": self._id}, new_val={"$set": {key: value}})

	def save_to_mongo(self):
		Database.insert(collection="books", data=self.json())


	@classmethod
	def get_all(cls):
		books = Database.find(collection="books", query=({}))
		return [cls(**book) for book in books]


	def json(self):
		return {
			"_id": self._id,
			"name": self.name,
			"href": self.href
		}


class Video():
	def __init__(self, name, href, _id=None):
		self.name = name
		self.href = href
		self._id = uuid.uuid4().hex if _id is None else _id

	@classmethod
	def search(cls, qs):
		videos = Database.search(collection="videos", qs=qs)
		return [cls(**video) for video in videos]

	@staticmethod
	def remove_fr_mongo(video_id):
		Database.remove(collection="videos", data={"_id": video_id})

	def update(self, key, value):
		Database.update(collection="videos", query={"_id": self._id}, new_val={"$set": {key: value}})


	def save_to_mongo(self):
		Database.insert(collection="videos", data=self.json())


	@classmethod
	def get_all(cls):
		videos = Database.find(collection="videos", query=({}))
		return [cls(**video) for video in videos]


	def json(self):
		return {
			"_id": self._id,
			"name": self.name,
			"href": self.href
		}


class Other():
	def __init__(self, name, href, _id=None):
		self.name = name
		self.href = href
		self._id = uuid.uuid4().hex if _id is None else _id


	@classmethod
	def search(cls, qs):
		others = Database.search(collection="others", qs=qs)
		return [cls(**other) for other in others]

	@staticmethod
	def remove_fr_mongo(other_id):
		Database.remove(collection="others", data={"_id": other_id})

	def update(self, key, value):
		Database.update(collection="others", query={"_id": self._id}, new_val={"$set": {key: value}})


	def save_to_mongo(self):
		Database.insert(collection="others", data=self.json())


	@classmethod
	def get_all(cls):
		others = Database.find(collection="others", query=({}))
		return [cls(**other) for other in others]


	def json(self):
		return {
			"_id": self._id,
			"name": self.name,
			"href": self.href
		}