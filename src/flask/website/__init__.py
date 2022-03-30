from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'sdbfsfnwodsnlf'

    from.config import config 
    from .cred import cred

    app.register_blueprint(config,url_prefix='/')
    app.register_blueprint(cred,url_prefix='/')


    return app 