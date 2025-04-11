from google.oauth2.service_account import Credentials
import json

from connectors.drive import DriveResourceMixin


class GoogleApisResourceMixin:
  """ Rules for acquiring Google API credentials."""

  SCOPES = [DriveResourceMixin.DRIVE_SERVICE_SCOPE]

  def get_service_account_info(self):
    return json.loads(self.service_account_json)

  def get_credentials(self):
    return Credentials.from_service_account_info(self.service_account_info, scopes=self.SCOPES)
