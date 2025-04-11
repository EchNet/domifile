# conftest.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(config=None):
  app = Flask(__name__)
  app.config.update({
      'SQLALCHEMY_DATABASE_URI': 'sqlite:///app.db',
      'SQLALCHEMY_TRACK_MODIFICATIONS': False,
  })
  if config:
    app.config.update(config)
  db.init_app(app)
  return app
