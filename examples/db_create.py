from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db = SQLAlchemy(app)


class Installation(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100), nullable=False)


def debug_create_tables():
  with app.app_context():
    print("Database URI:", app.config["SQLALCHEMY_DATABASE_URI"])
    print("Resolved Path:", os.path.abspath("db.sqlite3"))
    print("Metadata Tables:", db.metadata.tables)
    db.create_all()


if __name__ == "__main__":
  debug_create_tables()
