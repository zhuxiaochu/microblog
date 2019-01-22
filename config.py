import os 
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SRF_ENABLED = True
    SECRET_KEY = 'Could-you-please-tell-ME-when-to-go-home'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False