# DriveRetrieveMixin.py

import io
import logging
from googleapiclient.http import MediaIoBaseDownload

from connectors.drive.decorators import drive_file_id_operation
from connectors.drive.DriveFile import DriveFile
from connectors.drive.errors import http_error_handling

logger = logging.getLogger(__name__)


class DriveRetrieveMixin:
  """
    Wrapper for Google Drive services related to file data and metadata retrieval.
  """

  def __init__(self, drive_service):
    self.drive_service = drive_service

  def get(self, file_id):
    """ Fetch file metadata by file ID. """
    with http_error_handling(f"Retrieve file metadata {file_id}"):
      f = self.drive_service.files().get(fileId=file_id, fields=DriveFile.FIELDS_SPEC).execute()
      return DriveFile(f)

  @drive_file_id_operation()
  def download_file(self, file_id, output_path):
    """
      Download a file from Google Drive.
      
      Args:
          file_id (str): The ID of the Google Drive file.
          output_path (str): Local path to save the downloaded file.
      
      Returns:
          str: Path to the downloaded file.
    """
    with http_error_handling(f"Download file {file_id}"):
      request = self.drive_service.files().get_media(fileId=file_id)
      with io.FileIO(output_path, "wb") as file:
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while not done:
          status, done = downloader.next_chunk()
          logger.debug(f"Downloading {file_id} progress: {int(status.progress() * 100)}%")

    return output_path

    # TODO: balk at files that are beyond a certain size
