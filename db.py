# db.py
#
# Configure database and define models.
#
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
from flaskapp import flaskapp as app

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define allowed values of Installation.status
STATUS_OPTIONS = {'READY', 'IN_SERVICE', 'MARKED_FOR_TERMINATION', 'TERMINATED'}


# Define the Installation model
class Installation(db.Model):
  __tablename__ = 'installations'

  id = db.Column(db.Integer, primary_key=True)
  creator = db.Column(db.String(255), nullable=False)
  inbox_id = db.Column(db.String(255), nullable=False)
  service_account_info = db.Column(db.Text, nullable=False)
  when_created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
  status = db.Column(db.String(50), nullable=False, default='READY')

  def to_dict(self):
    return {
        'id': self.id,
        'creator': self.creator,
        'inbox_id': self.inbox_id,
        'service_account_info': json.loads(self.service_account_info),
        'when_created': self.when_created.isoformat(),
        'status': self.status
    }


# Create database tables (run this once to initialize the database)
@app.before_first_request
def create_tables():
  db.create_all()
