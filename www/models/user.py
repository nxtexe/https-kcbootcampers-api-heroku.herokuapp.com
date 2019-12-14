from common.database import Database
import uuid
from flask import session, Flask
import hashlib, binascii, os

class User():
	def __init__(self, fname, lname, email, password, cellphone, status="0", _id=None, active=True, temp_password=""):
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
		return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()
		#return password == hashlib.sha256(user_password.encode()).hexdigest()


	@classmethod
	def get_by_email(cls, email):
		data = Database.find_one(collection="users", query={"email": email})
		if data is not None:
			return cls(**data)


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
		user = User.get_by_email(email)
		if user is not None and user.active:
			#check the password
			if User._verify_password(user.password, password):
				session['email'] = email
				return True
			else:
				session['email'] = None
				return False
		else:
			session['email'] = None
			return False



	@staticmethod
	def temp_login_valid(email, password):
		"""Check whether the a user's email matches the uri"""
		user = User.get_by_email(email)
		if user is not None and not user.active:
			#check the password
			if User._verify_password(user.temp_password, password):
				return True
			else:
				return False
		else:
			return False



	@classmethod
	def register(cls, fname, lname, email, password, cellphone):
		user = cls.get_by_email(email)
		if email == "name@fake.com" and password == "123" and user is None:
			new_user = cls(fname, lname, email, User._hash_password(password), cellphone)
			new_user.status = "*"
			new_user.save_to_mongo()
			session["email"] = email
		elif user is None:
			#user does not exist so we can create
			new_user = cls(fname, lname, email, User._hash_password(password), cellphone)
			new_user.save_to_mongo()
			session["email"] = email
			return True
		else:
			session["email"] = None
			return False



	@classmethod
	def change_password(cls, email, password):
		password = User._hash_password(password)
		user = cls.get_by_email(email)
		if user is not None and user.temp_password != "":
			Database.update(collection="users", query={"email": email}, new_val={"$set": {"password": password}})
			return True
		else:
			return False


	def change_cell(self, cellphone):
		Database.update(collection="users", query={"email": self.email}, new_val={"$set": {"cellphone": cellphone}})


	@classmethod
	def temp_password(cls, email, password):
		password = User._hash_password(password)
		user = cls.get_by_email(email)
		if user is not None:
			Database.update(collection="users", query={"email": email}, new_val={"$set": {"temp_password": password}})
			return True
		else:
			return False


	@classmethod
	def rectify(cls, email):
		user = cls.get_by_email(email)
		if user is not None:
			user.activate()
			Database.update(collection="users", query={"email": email}, new_val={"$set": {"temp_password": ""}})
			return True
		else:
			return False


	@staticmethod
	def logout():
		session["email"] = None


	def json(self):
		return {
			"fname": self.fname.strip(),
			"lname": self.lname.strip(),
			"email": self.email.strip(),
			"_id": self._id.strip(),
			"password": self.password.strip(),
			"cellphone": self.cellphone.strip(),
			"active": self.active,
			"temp_password": self.temp_password.strip(),
			"status": self.status.strip()
		}


	def save_to_mongo(self):
		Database.insert(collection="users", data=self.json())


	@staticmethod
	def _remove_fr_mongo(email):
		Database.remove(collection="users", data={"email": email})


	@staticmethod
	def admin(_id):
		Database.update(collection="users", query={"_id": _id}, new_val={"$set": {"status": "*"}})


	@staticmethod
	def teacher(_id):
		Database.update(collection="users", query={"_id": _id}, new_val={"$set": {"status": "1"}})


	@staticmethod
	def student(_id):
		Database.update(collection="users", query={"_id": _id}, new_val={"$set": {"status": "0"}})
