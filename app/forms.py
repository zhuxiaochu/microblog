from flask_wtf import FlaskForm as Form
from wtforms.fields import StringField,TextField,TextAreaField,SubmitField,BooleanField
from wtforms.validators import DataRequired, Length

class LoginForm(Form):
	username = StringField(validators=[DataRequired(message='请输入用户名'), Length(max=15)],label='Username')
	password = StringField(validators=[DataRequired(), Length(max=15)])
	remember_me = BooleanField('remember me', default=False)
	submit = SubmitField('登录')

class SignUpForm(Form):
	username = StringField('请输入用户名',validators=[DataRequired(message='请输入用户名'), Length(max=15)])
	password = StringField(validators=[DataRequired(), Length(min=6,max=15)])
	submit = SubmitField('注册')

class EditForm(Form):
	username = TextField('username', validators = [DataRequired()])
	about_me = TextAreaField('about_me', validators = [Length(min = 0, max =140)])
	def __init__(self, original_username, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)
		self.original_username = original_username
	def validate(self):
		if not Form.validate(self):
			return False
		if self.username.data == self.original_username:
			return True
		user = User.query.filter_by(username = self.username.data).first()
		if user != None:
			return False
		return True

class ChangeForm(Form):
	title = TextField('title', validators = [DataRequired()])
	content = TextAreaField('content', validators = [Length(min = 0, max=140)])

class PostForm(Form):
	title = TextField('title', validators = [DataRequired(Length(min =0,max=120))])
	content = TextAreaField('content', validators = [Length(min = 0, max=1200)])