from common.database import Database
import uuid
import datetime
import time

class Post():
	def __init__(self, author, content, title,
						date_created=None, 
						_id=None,
						**kwargs):
		self.author = author
		self.title = title
		self.date_created = datetime.datetime.utcnow() if date_created is None else date_created
		self.content=content.strip()
		self._id = uuid.uuid4().hex if _id is None else _id
		self.short_form = self.content[:500]
		self.imgs = kwargs


	def save_to_mongo(self):
		Database.insert(collection="posts", data=self.json())


	@classmethod
	def get_all(cls):
		posts = Database.find(collection="posts", query=({}))
		return [cls(**post) for post in posts]

	@classmethod
	def get_by_email(cls, email):
		data = Database.find_one(collection="posts", query={"email": email})
		if data is not None:
			return cls(**data)


	@classmethod
	def get_by_id(cls, _id):
		data = Database.find_one(collection="posts", query={"_id": _id})
		if data is not None:
			return cls(**data)



	def json(self):
		return {
			"_id": self._id,
			"author": self.author,
			"content": self.content,
			"title": self.title,
			"date_created": self.date_created,
			"imgs": self.imgs
		}



	@staticmethod
	def remove_fr_mongo(post_id):
		Database.remove(collection="posts", data={"_id": post_id})


	def update(self, key, value):
		Database.update(collection="posts", query={"_id": self._id}, new_val={"$set": {key: value}})


	@classmethod
	def search(cls, qs):
		posts = Database.search(collection="posts", qs=qs)
		return [cls(**post) for post in posts]