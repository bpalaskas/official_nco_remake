from flask import Flask
from .main import main as main_blueprint
from .auth import auth as auth_blueprint
import logging
def create_app(config_class='config.Config'):
    app = Flask(__name__)
    app.config.from_object(config_class)
    logging.basicConfig(level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Register blueprints
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)

    return app
