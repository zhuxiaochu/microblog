from app import db
from app import login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5


ROLE_USER = 0     #regular user
ROLE_ADMIN = 1    #manager

@login.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

#for user
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


class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(100))
	content = db.Column(db.String(140))
	time = db.Column(db.DateTime, index=True, default=datetime.utcnow)     #value is function 
	user_id = db.Column(db.Integer,db.ForeignKey('user.id'))

	def __repr__(self):
		return '<Post %r>' % (self.body)


#for followers
followers = db.Table('followers',
	db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
	db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)
