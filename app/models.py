import jwt 
from app import db
from app import login
from app import app
from datetime import datetime
from time import time
from random import randint
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5


ROLE_USER = 0     #regular user
ROLE_ADMIN = 1    #manager

@login.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))


#create followers table
followers = db.Table('followers',
	db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
	db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


#create user orm
class User(UserMixin,db.Model):
	id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(64), index=True, unique = True)
	password_hash = db.Column(db.String(128))
	email = db.Column(db.String(120), index=True, unique=True)
	role = db.Column(db.SmallInteger, default = ROLE_USER)
	posts = db.relationship('Post', backref = 'author', lazy = 'dynamic')
	about_me = db.Column(db.String(140))
	last_seen = db.Column(db.DateTime)

	followed = db.relationship(
		'User', secondary=followers,
		primaryjoin=(followers.c.follower_id == id),
		secondaryjoin=(followers.c.followed_id == id ),
		backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

	def follow(self, user):
		if not self.is_following(user):
			self.followed.append(user)

	def unfollow(self, user):
		if self.is_following(user):
			self.followed.remove(user)

	def is_following(self, user):
		return self.followed.filter(
			followers.c.followed_id == user.id).count() > 0

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

	def avatar(self, size):
		digest = md5(self.email.lower().encode('utf-8')).hexdigest()
		return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest,size)	
		
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

	def get_reset_password_token(self, expires_in=600):
		return jwt.encode(
			{'reset_password': self.id, 'exp': time() + expires_in},
			app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

	@staticmethod
	def verify_reset_password_token(token):
		try:
			id = jwt.decode(token, app.config['SECRET_KEY'],
				            algorithms=['HS256'])['reset_password']
		except:
			return
		return User.query.get(id)

#create articles
class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(100))
	content = db.Column(db.String(140))                                    #140 won't limit text'length
	time = db.Column(db.DateTime, index=True, default=datetime.utcnow)     #value is function 
	user_id = db.Column(db.Integer,db.ForeignKey('user.id'))

	def __repr__(self):
		return '<Post %r>' % (self.title)


#verification code
#verify_code is not unique,usually it doesn't matter.
class RegistCode(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	verify_code = db.Column(db.Integer, index=True)
	email = db.Column(db.String(120), index=True, unique=True)

	def generate_code(self):
		code = randint(100000,999999)
		registcode = RegistCode.query.filter_by(verify_code=code).first()
		while registcode is not None:
			code = randint(1000000,9999999)
			registcode = RegistCode.query.filter_by(verify_code=code).first()
		self.verify_code = code


