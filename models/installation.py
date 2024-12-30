# installation.py
#
# Define the Installation model.
#
from flaskapp import flaskapp as app, db
from datetime import datetime
from forms import FormValidator
from utils import validate_email, validate_drive_file_id, validate_json
import json


class Installation(db.Model):
  """
  """
  __tablename__ = 'installations'

  # Define allowed values of Installation.status
  class Status:
    READY = 'READY'
    IN_SERVICE = 'IN_SERVICE',
    MARKED_FOR_TERMINATION = 'MARKED_FOR_TERMINATION'
    TERMINATED = 'TERMINATED'
    BLOCKED = 'BLOCKED'

  id = db.Column(db.Integer, primary_key=True)
  creator = db.Column(db.String(255), nullable=False, index=True)
  root_folder_id = db.Column(db.String(255), nullable=False, index=True, unique=True)
  service_account_info = db.Column(db.Text, nullable=False)
  when_created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
  status = db.Column(db.String(50), nullable=False, default=Status.READY, index=True)
  last_refresh = db.Column(db.DateTime, nullable=True)

  def to_dict(self):
    return {
        'id': self.id,
        'creator': self.creator,
        'root_folder_id': self.root_folder_id,
        'service_account_info': self.service_account_info,
        'when_created': self.when_created.isoformat(),
        'status': self.status,
        'last_refresh': self.last_refresh.isoformat(),
    }

  @classmethod
  def create(cls, values, commit=True):
    #
    # Permitted values keys: creator, root_folder_id, service_account_info
    #
    # TODO: encrypt the service account credentials
    #
    new_installation = Installation(**values)
    db.session.add(new_installation)
    if commit:
      db.session.commit()
    return new_installation

  def update_status(self, new_status, commit=True):
    self.status = new_status
    db.session.add(self)
    if commit:
      db.session.commit()
    return self

  def update_last_refresh(self, commit=True):
    self.last_refresh = datetime.utcnow
    db.session.add(self)
    if commit:
      db.session.commit()
    return self


#
# Validator
#
def validate_installation_values(values):
  FormValidator(
      required_fields=['creator', 'root_folder_id', 'service_account_info']).validate(values)
  validate_email(values["creator"])
  validate_drive_file_id(values["root_folder_id"])
  validate_json(values["service_account_info"])
  return values


#
# Management/API command
#
def create_installation(creator, root_folder_id, service_account_filename):
  """
  """
  with app.app_context():

    with open(service_account_filename, "r") as f:
      service_account_info = f.read()

    values = validate_installation_values({
        "creator": creator,
        "root_folder_id": root_folder_id,
        "service_account_info": service_account_info,
    })

    return Installation.create(values)
