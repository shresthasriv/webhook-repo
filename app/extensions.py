from flask_pymongo import PyMongo

# Setup MongoDB here
mongo = PyMongo()

def init_db(app):
    mongo_uri = 'mongodb+srv://loverofdogs2004:test@techstax.ni0ef3w.mongodb.net/github_webhooks?retryWrites=true&w=majority&appName=techstax'
    app.config['MONGO_URI'] = mongo_uri

    mongo.init_app(app)
