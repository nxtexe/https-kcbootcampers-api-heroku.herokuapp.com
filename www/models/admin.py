from common.database import Database
from .user import User
import uuid
from flask import session, Flask
import hashlib, binascii, os

class Admin():
	def __init__(self, fname, lname, email, password, cellphone, status, _id=None, active=True, temp_password=""):
		self.fname = fname
		self.lname = lname
		self.email = email
		self.password = password
		self.cellphone = cellphone
		self._id = uuid.uuid4().hex if _id is None else _id
		self.active = active
		self.temp_password = temp_password
		self.status = status
		

	@staticmethod
	def _hash_password(password):
		#uuid is used to generate a random number
		salt = uuid.uuid4().hex
		return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt
		#return hashlib.sha256(password.encode()).hexdigest()


	@staticmethod
	def _verify_password(hashed_password, user_password):
		password, salt = hashed_password.split(':')
		#password = hashed_password
		#print("Hashed Password:", hashed_password)
		#print("Provided Password", hashlib.sha256(user_password.encode()).hexdigest())
		return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()
		#return password == hashlib.sha256(user_password.encode()).hexdigest()


	@classmethod
	def get_by_email(cls, email):
		data = Database.find_one(collection="users", query={"email": email})
		if data is not None:
			return cls(**data)


	@classmethod
	def get_all(cls):
		users = Database.find(collection="users", query=({}))
		return [cls(**user) for user in users]


	@staticmethod
	def activate_all():
		users = Admin.get_all()
		[user.activate() for user in users]


	@staticmethod
	def deactivate_all():
		users = Admin.get_all()
		[user.deactivate() if user.email != "name@fake.com" else user for user in users]


	@staticmethod
	def deactivate_one(email):
		user = User.get_by_email(email)
		user.deactivate()


	@staticmethod
	def activate_one(email):
		user = User.get_by_email(email)
		user.deactivate


	def activate(self):
		Database.update(collection="users", query={"email": self.email}, new_val={"$set": {"active": True}})


	def deactivate(self):
		Database.update(collection="users", query={"email": self.email}, new_val={"$set": {"active": False}})


	@classmethod
	def get_by_id(cls, _id):
		data = Database.find_one(collection="users", query={"_id": _id})
		if data is not None:
			return cls(**data)


	@staticmethod
	def login_valid(email, password):
		"""Check whether the a user's email matches the password they sent us"""
		admin = Admin.get_by_email(email)
		if admin is not None and admin.active:
			#check the password
			if Admin._verify_password(admin.password, password):
				return True
			else:
				return False
		else:
			return False



	@staticmethod
	def temp_login_valid(email, password):
		"""Check whether the a user's email matches the uri"""
		admin = Admin.get_by_email(email)
		if admin is not None and not admin.active and admin.status == "*":
			#check the password
			if Admin._verify_password(admin.temp_password, password):
				return True
			else:
				return False
		else:
			return False



	@classmethod
	def register(cls, fname, lname, email, password, cellphone):
		admin = cls.get_by_email(email)
		if admin is None:
			#user does not exist so we can create
			new_admin = cls(fname, lname, email, User._hash_password(password), cellphone)
			new_admin.save_to_mongo()
			session["email"] = email
			return True
		else:
			session["email"] = None
			return False



	@classmethod
	def change_password(cls, email, password):
		password = User._hash_password(password)
		admin = cls.get_by_email(email)
		if admin is not None:
			Database.update(collection="users", query={"email": email}, new_val={"$set": {"password": password}})
			return True
		else:
			return False


	@classmethod
	def temp_password(cls, email, password):
		password = User._hash_password(password)
		admin = cls.get_by_email(email)
		if admin is not None:
			Database.update(collection="users", query={"email": email}, new_val={"$set": {"temp_password": password}})
			return True
		else:
			return False


	@classmethod
	def rectify(cls, email):
		admin = cls.get_by_email(email)
		if admin is not None:
			admin.activate()
			Database.update(collection="users", query={"email": email}, new_val={"$set": {"temp_password": ""}})
			return True
		else:
			return False


	@staticmethod
	def logout():
		session["email"] = None


	def json(self):
		return {
			"fname": self.fname,
			"lname": self.lname,
			"email": self.email,
			"_id": self._id,
			"password": self.password,
			"cellphone": self.cellphone,
			"active": self.active,
			"last_pass": self.last_pass,
			"status": self.status
		}


	def save_to_mongo(self):
		Database.insert(collection="users", data=self.json())


	@staticmethod
	def _remove_fr_mongo(email):
		Database.remove(collection="users", data={"email": email})
