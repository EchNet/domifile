# api_key.py
#
# Define the ApiKey model.
#
from datetime import datetime, UTC
from flaskapp import db
from utils import generate_token, validate_email


# ApiKey model.
class ApiKey(db.Model):
  __tablename__ = 'apikeys'

  # Values of ApiKey.status
  class Status:
    ACTIVE = 'ACTIVE'
    EXPIRED = 'EXPIRED'

  id = db.Column(db.Integer, primary_key=True)
  token = db.Column(db.String(255), nullable=False, index=True, unique=True)
  email = db.Column(db.String(255), nullable=False)
  when_created = db.Column(db.DateTime(timezone=True),
                           default=lambda: datetime.now(UTC),
                           nullable=False)
  status = db.Column(db.String(50), nullable=False, default=Status.ACTIVE)

  IDENT_FIELDS = ("id", "key", "email")

  def to_dict(self):
    return {
        'id': self.id,
        'token': self.token,
        'email': self.email,
        'when_created': self.when_created.isoformat(),
        'status': self.status
    }

  def expire(self, commit=True):
    #
    # Render this ApiKey invalid.
    #
    self.status = self.Status.EXPIRED
    db.session.add(self)
    if commit:
      db.session.commit()
    return self

  @classmethod
  def create(cls, values, commit=True):
    #
    # Create a new ApiKey.
    #
    # Parameters
    #
    # value (str): The initial field values.  Required: token, email.
    #
    # commit (bool): True to commit immediately.  Default is true.
    #
    new_api_key = ApiKey(**values, status=cls.Status.ACTIVE)
    db.session.add(new_api_key)
    if commit:
      db.session.commit()
    return new_api_key

  @classmethod
  def token_exists(cls, token):
    return db.session.query(exists().where(cls.token == token)).scalar()


#
# Management command.
#
def create_api_key(email):
  while True:
    if not ApiKey.token_exists(token):
      values = {
          "token": token,
          "email": email,
      }
      return ApiKey.create(values)


#
# Management command.
#
def expire_api_key(ident):
  expire_count = 0
  for field in ApiKey.IDENT_FIELDS:
    api_keys = ApiKey.query.filter_by(**{field: ident})
    for api_key in api_keys:
      if api_key.status == ApiKey.Status.EXPIRED:
        print(f"{api_key.token} already expired.")
      else:
        api_key.expire()
        print(f"{api_key.token} expired.")
      expire_count += 1
  if expire_count == 0:
    print("No such API key")
