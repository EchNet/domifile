from app import app
from flask_sqlalchemy import SQLAlchemy

#
# Database
#
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
db = SQLAlchemy(app)
