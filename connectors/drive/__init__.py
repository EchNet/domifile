# connectors/drive/__init__.py

from googleapiclient.discovery import build

from connectors.drive.DriveConnector import DriveConnector


class DriveResourceMixin:
  """ Rules for constructing an authenticated Drive API client. """

  DRIVE_SERVICE_NAME = "drive"
  DRIVE_SERVICE_VERSION = "v3"
  DRIVE_SERVICE_SCOPE = "https://www.googleapis.com/auth/drive"

  def get_drive_service(self):
    return build(self.DRIVE_SERVICE_NAME,
                 self.DRIVE_SERVICE_VERSION,
                 credentials=self.credentials,
                 cache_discovery=False)

  def get_drive_connector(self):
    return DriveConnector(self.drive_service)
