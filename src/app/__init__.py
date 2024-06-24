from flask import Flask
from .config import Config
from .routes.api import api_bp
from .routes.config import config_bp
from .routes.control import control_bp
from .routes.healthcheck import healthcheck_bp
from .routes.memory import memory_bp

def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(config_bp, url_prefix='/api')
    app.register_blueprint(control_bp, url_prefix='/api')
    app.register_blueprint(healthcheck_bp, url_prefix='/api')
    app.register_blueprint(memory_bp, url_prefix='/api')

    return app
