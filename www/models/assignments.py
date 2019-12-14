from common.database import Database
import uuid
import datetime
import time


class Assignment():
	def __init__(self, author, content, title, date_due, date_created=None, _id=None, **kwargs):
		self.author = author
		self.title = title
		self.date_created = datetime.datetime.utcnow() if date_created is None else date_created
		self.date_due = date_due
		self.content=content.strip()
		self._id = uuid.uuid4().hex if _id is None else _id
		self.short_form = self.content[:500]
		self.imgs = kwargs


	def save_to_mongo(self):
		Database.insert(collection="assignments", data=self.json())


	@classmethod
	def get_all(cls):
		assignments = Database.find(collection="assignments", query=({}))
		return [cls(**assignment) for assignment in assignments]

	@classmethod
	def get_by_email(cls, email):
		data = Database.find_one(collection="assignments", query={"email": email})
		if data is not None:
			return cls(**data)


	@classmethod
	def get_by_id(cls, _id):
		data = Database.find_one(collection="assignments", query={"_id": _id})
		if data is not None:
			return cls(**data)



	def json(self):
		return {
			"_id": self._id,
			"author": self.author,
			"content": self.content,
			"title": self.title,
			"date_created": self.date_created,
			"date_due": self.date_due,
			'imgs': self.imgs
		}

	@staticmethod
	def remove_fr_mongo(assignment_id):
		Database.remove(collection="assignments", data={"_id": assignment_id})


	def update(self, key, value):
		Database.update(collection="assignments", query={"_id": self._id}, new_val={"$set": {key: value}})


	@classmethod
	def search(cls, qs):
		assignments = Database.search(collection="assignments", qs=qs)
		return [cls(**assignment) for assignment in assignments]