from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db_url = 'postgresql://postgres:postgres@localhost:5432/postgres'
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # initialize database
    db.init_app(app)
    return app

