# DriveUpdateMixin.py

import logging
from googleapiclient.errors import HttpError

from connectors.drive.errors import http_error_handling

logger = logging.getLogger(__name__)


class DriveUpdateMixin:
  """
    Wrapper for Google Drive services related to file updates.
  """

  def __init__(self, drive_service):
    self.drive_service = drive_service

  def move_file(file_id, new_parent_id):
    """
      Move the file identified by file_id to the folder identified by new_parent_id.
    """
    # Retrieve the file metadata
    with http_error_handling(f"Looking up file {file_id}"):
      file_metadata = self.drive_service.files().get(fileId=file_id, fields="parents").execute()

    # Remove the file from its current parent folder(s), while adding the new parent.
    previous_parents = ",".join(file_metadata.get("parents", []))

    with http_error_handling(f"Moving file {file_id} to folder {new_parent_id}"):
      self.drive_service.files().update(
          fileId=spreadsheet_id,
          addParents=new_parent_id,
          removeParents=previous_parents,
      ).execute()

  def update_file_owner(self, file_id, new_owner_email):
    """
     Change ownership of a Google Drive file.

     Note: changes in ownership are limited to between users in the same Google
     Workspace organization.

      Args:
          file_id (str): ID of the file
          new_owner_email (str): Email address of the desired owner

      Returns:
        True if the ownership change succeeded.
    """
    with http_error_handling(f"Transferring ownership of file {file_id} to {new_owner_email}"):
      try:
        self.drive_service.permissions().create(
            fileId=file_id,
            body={
                'type': 'user',
                'role': 'owner',
                'emailAddress': new_owner_email,
            },
            transferOwnership=True,
        ).execute()
      except HttpError as http_error:
        error_code = http_error.resp.status
        if error_code == 405:  # TODO: determine true tell.
          logger.warn(f"Drive: WARNING: ownership not transferred - {http_error}")
          return False
        else:
          raise
    return True

  def update_file_properties(self, file_id, properties):
    """
    """
    assert isinstance(properties, dict), "properties must be a dict"
    with http_error_handling(f"Set properties={properties} on file={file_id}"):
      self.drive_service.files().update(
          fileId=file_id,
          body={
              "properties": properties
          },
      ).execute()
