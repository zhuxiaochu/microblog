from flask_wtf import FlaskForm as Form
from app.models import User
from wtforms.fields import (StringField,TextField,TextAreaField,SubmitField,BooleanField,
                            PasswordField)
from wtforms.validators import DataRequired, Length, ValidationError, Email, EqualTo

class LoginForm(Form):
    username = StringField(validators=[DataRequired(), Length(max=25)],label='Username')
    password = StringField(validators=[DataRequired(), Length(max=15)])
    remember_me = BooleanField('check', default=False)
    submit = SubmitField('登录')

class SignUpForm(Form):
    username = StringField('username',validators=[DataRequired(message='请输入用户名'), Length(max=25)])
    email = StringField('Email', validators=[DataRequired(), Email(message='不合理的邮箱格式')])
    password = PasswordField('password', validators=[DataRequired(), Length(min=6,max=15)])
    password2 = PasswordField('password2', validators=[DataRequired(), EqualTo('password',
                             message='前后输入的密码不一样')])
    submit = SubmitField('注册')

    def validate_username(self,username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('用户名已存在')
    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('此邮箱已注册')


class EditProfileForm(Form):
    """docstring for EditProfileForm"""
    username = StringField('用户名', validators=[DataRequired()])        
    about_me = TextAreaField('个人简介', validators=[Length(min=0,max=140)])
    submit = SubmitField('保存')

			
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