# DriveCreateMixin.py

import logging
from googleapiclient.errors import HttpError

from connectors.drive.errors import http_error_handling
from connectors.drive.DriveFile import DriveFile

logger = logging.getLogger(__name__)


class DriveCreateMixin:
  """
    Wrapper for Google Drive services related to file creation.
  """

  def create_folder(self, name, *, parent, properties={}):
    """
      Create a folder in Google Drive.

      Args:
          name (str): Name of the new folder.
          parent (str): ID of the parent folder.
          owners (str, optional): Email address of the desired owner

      Returns:
          str: The ID of the created folder.
    """

    # Create the folder
    with http_error_handling(f"Creating new folder {name}"):
      folder = self.drive_service.files().create(
          body={
              "name": name,
              "mimeType": DriveFile.FOLDER_MIME_TYPE,
              "parents": [parent],
              "properties": properties,
          },
          fields=DriveFile.FIELDS_SPEC,
      ).execute()

    return DriveFile(folder)
