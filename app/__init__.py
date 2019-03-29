import os 
import logging
import flask_whooshalchemyplus
import smtplib

from logging.handlers import SMTPHandler
from logging.handlers import RotatingFileHandler

from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_ckeditor import CKEditor
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_apscheduler import APScheduler
from flask_talisman import Talisman
from flask_redis import Redis


app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app,db)

login = LoginManager(app)
login.setup_app(app)
login.login_view = 'login'           #visit 'login_required' when not logged in,redirect to '/login'
login.login_message = '先登录，好吗？'

ckeditor = CKEditor(app)
csrf = CSRFProtect(app)
csp = {
    'default-src': [
        '\'self\'',
        'fonts.googleapis.com',
        '*.gstatic.com'
    ],
    'img-src': '*',
    'style-src': [
        '\'self\'',
        '*.googleapis.com',
        '*.gstatic.com'
    ]
}
#Talisman(app, force_https_permanent=True,
#   content_security_policy=csp,
#   content_security_policy_nonce_in=['script-src','style-src'])

limiter = Limiter(app, key_func=get_remote_address)

class SSLSMTPHandler(SMTPHandler):
    def emit(self, record):
        """
        Emit a record.
        """
        try:
            port = self.mailport
            if not port:
                port = smtplib.SMTP_PORT
            smtp = smtplib.SMTP_SSL(self.mailhost, port)
            msg = self.format(record)
            if self.username:
                smtp.login(self.username, self.password)
            smtp.sendmail(self.fromaddr, self.toaddrs, msg)
            smtp.quit()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

if not app.debug and not app.config['TEST']:
    #send a email for errors
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_SSL']:
            secure = ()
        mail_handler = SSLSMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr=app.config['MAIL_USERNAME'],
            toaddrs=app.config['ADMINS'], subject='Microblog errors',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

#save logs in local files
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=102400,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('Miroblog startup~~~~~~~')

mail = Mail(app)

redis1 = Redis(app)

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()


from app import routes,models

flask_whooshalchemyplus.init_app(app)  #strange use
