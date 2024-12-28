# db.py
#
# Configure database and define models.
#
from flask_sqlalchemy import SQLAlchemy
from flaskapp import flaskapp as app

#
# App configuration settings pertinent to the database.
#
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#
# Initialize SQLAlchemy.
#
db = SQLAlchemy(app)


# Create database tables (run this once to initialize the database)
def create_tables():
  db.create_all()
