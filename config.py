import os 
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    '''all important params should be set properly'''
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