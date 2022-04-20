from flask import Flask
from config import flask_config
from app.unicon.main import main

def create_app():
    '''returns a flask app
        
    Returns:
        app (flask app): the initialized app
    '''
    app = Flask(__name__)
    app.config.from_object(flask_config)

    # add routes from main sub directory
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app

# main()