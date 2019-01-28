from threading import Thread
from flask import render_template
from flask_mail import Message
from app import mail, app

def send_async_email(app, msg):
    with app.app_context():
      mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=app(app, msg)).start()

#I use 163 mail
def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[Microblog] 重置你的密码',
               sender=("1956\'blog", app.config['ADMINS']),
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))

def send_verify_code_email(input_email,code):
  send_email('[Microblog]验证码',
             sender=("1956\'blog", app.config['ADMINS']),
             recipients=[input_email],
             text_body='你的验证码：'+str(code),
             html_body='<p>你的验证码：{}</p>'.format(code))