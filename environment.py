# environment.py
#
# Extract configuration values from environment variables.
#
import json
import os
from google.oauth2.service_account import Credentials


class ServiceAccountInfo:

  @classmethod
  def from_json_string(Cls, json_string, json_source="JSON string"):
    try:
      obj = json.loads(json_string)
    except e as Exception:
      raise Exception(f"Invalid JSON in {json_source}") from e
    return Cls(obj)

  @classmethod
  def from_env(Cls, env_key):
    if env_key not in os.environ:
      raise EnvironmentError(f"The {env_key} environment variable is not set.")
    json_string = os.environ[env_key]
    return Cls.from_json_string(json_string, f"env var {env_key}")

  @classmethod
  def from_file(Cls, filename):
    cred_source = Cls()
    with open(filename, "r") as f:
      json_string = f.read()
    return Cls.from_json_string(json_string, f"file {filename}")

  def __init__(self, sa_info_obj):
    self.sa_info_obj = sa_info_obj

  @property
  def parsed(self):
    return self.sa_info_obj

  def get_scoped_credentials(self, scopes):
    return Credentials.from_service_account_info(self.sa_info_obj, scopes=scopes)
