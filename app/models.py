from app import db
from app import login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


ROLE_USER = 0     #regular user
ROLE_ADMIN = 1    #manager

@login.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))


class User(UserMixin,db.Model):
	id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(64), index=True, unique = True)
	password_hash = db.Column(db.String(128))
	email = db.Column(db.String(120), index=True, unique=True)
	role = db.Column(db.SmallInteger, default = ROLE_USER)
	posts = db.relationship('Post', backref = 'author', lazy = 'dynamic')
	about_me = db.Column(db.String(140))
	last_seen = db.Column(db.DateTime)

	def set_password(self,password):
		self.password_hash = generate_password_hash(password)

	def check_password(self,password):
		return check_password_hash(self.password_hash, password)

	def __repr__(self):
		return '<User %r>' % (self.username)

	@classmethod
	def login_check(cls,username):
		user = cls.query.filter(User.username == username).first()
		if not user:
			user = cls.query.filter(User.email == username).first()
			if not user:
				return None
		return user

class Post(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	title = db.Column(db.String(100))
	content = db.Column(db.String(140))
	time = db.Column(db.DateTime, index=True, default=datetime.utcnow)     #value is function 
	user_id = db.Column(db.Integer,db.ForeignKey('user.id'))

	def __repr__(self):
		return '<Post %r>' % (self.body)