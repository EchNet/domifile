# DriveDeleteMixin.py

from connectors.drive.errors import http_error_handling
from connectors.drive.decorators import drive_file_id_operation


class DriveDeleteMixin:
  """
    Wrapper for Google Drive services related to file deletion.
  """

  def __init__(self, drive_service):
    self.drive_service = drive_service

  @drive_file_id_operation()
  def delete_file(self, file_id):
    """
      Permanently delete a file from Google Drive.

      Args:
          file_id (str): The DriveFile or ID of the file to delete.

      Returns:
          (none)
    """
    with http_error_handling(f"Deleting file {file_id}"):
      self.drive_service.files().delete(fileId=file_id).execute()

  @drive_file_id_operation()
  def trash_file(self, file_id):
    """
      Move a file in Google Drive into the trash.

      Args:
          file_id (str): The DriveFile or ID of the file to delete.

      Returns:
          (none)
    """
    with http_error_handling(f"Trashing file {file_id}"):
      self.drive_service.files().update(fileId=file_id, body={"trashed": True}).execute()
