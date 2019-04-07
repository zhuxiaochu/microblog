import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir,'.env'))

class Config(object):
    '''all important params should be set properly'''
    SEND_FILE_MAX_AGE_DEFAULT = 432000
    SRF_ENABLED = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or \
        'Could-you-please-tell-ME-when-to-go-home'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    #mail configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = os.environ.get('MAIL_PORT')
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = os.environ.get('ADMINS')
    #others
    DATABASE_ADMIN = os.environ.get('DATABASE_ADMIN')         #control content of index.html
    NO_EMAIL = os.environ.get('NO_EMAIL') is not None   #stop sending verification
    #ckeditor configuration
    CKEDITOR_ENABLE_CSRF = True
    CKEDITOR_ENABLE_CODESNIPPET = True
    CKEDITOR_FILE_UPLOADER = 'upload'
    CKEDITOR_SERVE_LOCAL = True
    UPLOADED_PATH = os.path.join(basedir,'pictures','ckeditor')

    #scheduler  use server location time.
    JOBS = [
        {
            'id': 'clearimage',
            'func': 'app.dbmanage:clear_image',
            'trigger': 'cron',
            'day_of_week': 0,
            'hour': 1,
            'minute': 5
        }
    ]
    SCHEDULER_API_ENABLED = True
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE')\
        is not None
    #flask-login
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    #flask-wtf
    WTF_CSRF_TIME_LIMIT = 28800 #eight hours,means that you shouldn't \
                                #write an article for more than eight hours
    POST_PER_PAGE = 15  #articel num in index.html
    #flask-whooshsqlalchemyplus
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    #redis
    REDIS_HOST = os.environ.get('REDIS_HOST') or 'localhost'
    REDIS_PORT = os.environ.get('REDIS_PORT') or 6379
    REDIS_DB = os.environ.get('REDIS_DB') or 0
    REDIS_DISABLE = os.environ.get('REDIS_DISABLE') is not None

    DEBUG_QUERY = os.environ.get('DEBUG_QUERY') is not None
    PROFILER = os.environ.get('PROFILER') is not None

    TEST = os.environ.get('TEST') is None

    #get the exclusive url from baidu  problom exists!
    BAIDU_LINKSUBMIT = os.environ.get('BAIDU_LINKSUBMIT')
