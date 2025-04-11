# DriveCreateMixin.py

import logging
import os
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from connectors.drive.decorators import drive_file_id_operation
from connectors.drive.errors import http_error_handling
from connectors.drive.DriveFile import DriveFile

logger = logging.getLogger(__name__)


class DriveCreateMixin:
  """
    Wrapper for Google Drive services related to file creation.
  """

  @drive_file_id_operation()
  def create_folder(self, name, *, parent, properties={}):
    """
      Create a folder in Google Drive.

      Args:
          name (str): Name of the new folder.
          parent (str, optional): ID of the parent folder.
          properties (dict, optional): Meta-properties.

      Returns:
          str: A DriveFile that represents the created folder.
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

  #=================================================================
  # upload_file
  #=================================================================

  @drive_file_id_operation()
  def upload_file(self, file_path, *, parent, mime_type=None, properties={}):
    """
      Copy a local file to Drive.
    """
    file_name = os.path.basename(file_path)

    file_metadata = {
        'name': file_name,
        'parents': [parent if isinstance(parent, str) else parent.id]
    }
    media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)

    uploaded_file = self.drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields=DriveFile.FIELDS_SPEC,
    ).execute()

    return DriveFile(uploaded_file)
