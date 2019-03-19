import jwt 
import secrets
import flask_whooshalchemyplus
from app import db, redis1, login
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

#post_tag_relationship
p_tag_rel = db.Table('p_tag_rel',
	db.Column('tag_id', db.Integer, db.ForeignKey('post_tag.id')),
	db.Column('post_id', db.Integer, db.ForeignKey('post.id'))
)

#create user orm
class User(UserMixin,db.Model):
	id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(64), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	email = db.Column(db.String(120), index=True, unique=True)
	role = db.Column(db.SmallInteger, default = ROLE_USER)
	posts = db.relationship('Post', backref = 'author', lazy='dynamic')
	about_me = db.Column(db.String(140))
	last_seen = db.Column(db.DateTime)
	login_record = db.relationship('LoginRecord', backref='owner',
		lazy='dynamic')
	upload_image = db.relationship('UploadImage', backref='uploader',
		lazy='dynamic')
	leave_message = db.relationship('LeaveMessage', backref='author',
		lazy='dynamic')

	followed = db.relationship(
		'User', secondary=followers,
		primaryjoin=(followers.c.follower_id == id),
		secondaryjoin=(followers.c.followed_id == id),
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
		return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
			digest,size)	
		
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
	__searchable__ = ['title', 'content']

	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(128))
	content = db.Column(db.String(20000))                                    #autoincrease
	time = db.Column(db.DateTime, index=True, default=datetime.utcnow)     #value is function 
	last_modify = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	cat_id = db.Column(db.Integer, db.ForeignKey('post_cat.id'))
	tags = db.relationship('PostTag',
		secondary=p_tag_rel,
		backref=db.backref('posts', lazy='dynamic'), lazy='dynamic')

	def __repr__(self):
		return '<Post {0}>'.format(self.title)


#verification code
#verify_code is not unique,usually it doesn't matter.
class RegistCode(db.Model):
	'''code-email table'''
	id = db.Column(db.Integer, primary_key=True)
	verify_code = db.Column(db.String(16), index=True)
	email = db.Column(db.String(120), index=True, unique=True)

	def code_method(self):
		#return randint(10000000,99999999)
		return secrets.token_hex(3)

	def generate_code(self):
		code = self.code_method()  #can add something use secrets module
		registcode = RegistCode.query.filter_by(verify_code=code).first()
		while registcode is not None:
			code = self.code_method()
			registcode = RegistCode.query.filter_by(verify_code=code).first()
		self.verify_code = code

	def __repr__(self):
		return '<RegistCode %r>' % (self.email)


class LoginRecord(db.Model):
	'''login record'''
	id = db.Column(db.Integer, primary_key=True)
	login_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	login_ip = db.Column(db.String(32))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


	def __repr__(self):
		return '<LoginRecord %r>' % (self.owner.username)


class UploadImage(db.Model):
	'''mark image,mark=0 means image can be deleted later'''
	id = db.Column(db.Integer, primary_key=True)
	image_path = db.Column(db.String(256))
	image_name = db.Column(db.String(48))
	upload_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	mark = db.Column(db.Integer, index=True, default=0)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __repr__(self):
		return '<UploadImage %r>' % (self.uploader.username)


class LeaveMessage(db.Model):
	'''message board'''
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(12))
	content = db.Column(db.String(210))
	email = db.Column(db.String(48), index=True)
	leave_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)     #value is function 
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __repr__(self):
		if self.user_id:
			return '<LeaveMessage %r>' % (self.author.username)
		else:
			return '<LeaveMessage %r>' % (self.name)


class PostCat(db.Model):
	'''category for post'''
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(12))
	posts = db.relationship('Post', backref='cat', lazy='dynamic')

	def __repr__(self):
		return '<PostCat %r>' % (self.name)


class PostTag(db.Model):
	'''tags for post'''
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(12))

	def __repr__(self):
		return '<PostTag {0}>'.format(self.name)


class Use_Redis(object):

	@classmethod
	def set(cls, *args, disable=False):
		if not disable:
			*keys, value = args
			if not keys:
				raise TypeError('need at least two arguments')
			key = '_'.join(*keys)
			return redis1.set(key, value)
		else:
			return 

	@classmethod
	def get(cls, *args, disable=False):
		if not disable:
			key = '_'.join(*args)
			return redis1.get(key)
		else:
			return 

	def __repr__(self):
		return '<redis_custom_tool>'