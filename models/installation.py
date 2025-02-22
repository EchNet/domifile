# installation.py
#
# Define the Installation model.
#
from db import db
from datetime import datetime
from forms import FormValidator
from utils import validate_email, validate_drive_file_id, validate_json


class Installation(db.Model):
  """
  """
  __tablename__ = 'installations'

  # Define allowed values of Installation.status
  class Status:
    READY = 'READY'
    IN_SERVICE = 'IN_SERVICE'
    MARKED_FOR_TERMINATION = 'MARKED_FOR_TERMINATION'
    TERMINATED = 'TERMINATED'
    BLOCKED = 'BLOCKED'

  id = db.Column(db.Integer, primary_key=True)
  creator = db.Column(db.String(255), nullable=False, index=True)
  root_folder_id = db.Column(db.String(255), nullable=False, index=True, unique=True)
  inbox_watcher_resource_id = db.Column(db.String(255), nullable=True)
  service_account_info = db.Column(db.Text, nullable=False)
  when_created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
  status = db.Column(db.String(50), nullable=False, default=Status.READY, index=True)
  last_refresh = db.Column(db.DateTime, nullable=True)

  def to_dict(self):
    return {
        'id': self.id,
        'creator': self.creator,
        'root_folder_id': self.root_folder_id,
        'inbox_watcher_resource_id': self.inbox_watcher_resource_id,
        'service_account_info': self.service_account_info,
        'when_created': self.when_created.isoformat(),
        'status': self.status,
        'last_refresh': self.last_refresh.isoformat(),
    }

  @classmethod
  def get_by_root_folder_id(cls, root_folder_id):
    # There can be only one, due to uniqueness constraint.
    return cls.query.filter_by(root_folder_id=root_folder_id).first()

  @classmethod
  def create(cls, values, commit=True):
    """
      Permitted values keys: creator, root_folder_id, service_account_info
      TODO: encrypt the service account credentials
    """
    new_installation = Installation(**values)
    db.session.add(new_installation)
    if commit:
      db.session.commit()
    return new_installation

  def update(self, values={}, commit=True):
    for key, value in values.items():
      if key == "last_refresh":
        value = datetime.utcnow()
      setattr(self, key, value)
    db.session.add(self)
    if commit:
      db.session.commit()
    return self

  @staticmethod
  def validate_installation_values(values):
    FormValidator(
        required_fields=['creator', 'root_folder_id', 'service_account_info']).validate(values)
    validate_email(values["creator"])
    validate_drive_file_id(values["root_folder_id"])
    validate_json(values["service_account_info"])
    return values
