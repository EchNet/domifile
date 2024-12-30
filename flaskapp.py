# flaskapp.py
#
# Initialize Flask app and database.
#
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

flaskapp = Flask(__name__)

#
# App configuration settings pertinent to the database.
#
flaskapp.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.abspath('db.sqlite3')}"
flaskapp.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
flaskapp.config['SQLALCHEMY_ECHO'] = False  # Set True to debug

#
# Initialize SQLAlchemy.
#
db = SQLAlchemy(flaskapp)
