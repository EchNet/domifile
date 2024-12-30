from flaskapp import flaskapp as app, db
from .installation import Installation
from .api_key import ApiKey


#
# Management command.
#
def create_tables():
  """
    Create database tables.
  """
  print("Creating tables...")
  with app.app_context():
    db.create_all()
