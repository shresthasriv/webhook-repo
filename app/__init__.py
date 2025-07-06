from flask import Flask
from flask_cors import CORS

from app.webhook.routes import webhook
from app.extensions import init_db


# Creating our flask app
def create_app():

    app = Flask(__name__)
    
    # Enable CORS for all routes
    CORS(app)
    
    # Initialize MongoDB
    init_db(app)
    
    # registering all the blueprints
    app.register_blueprint(webhook)
    
    return app
