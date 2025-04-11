# DriveUpdateMixin.py

import logging
from googleapiclient.errors import HttpError

from connectors.drive.decorators import drive_file_id_operation
from connectors.drive.DriveFile import DriveFile
from connectors.drive.errors import http_error_handling

logger = logging.getLogger(__name__)


class DriveUpdateMixin:
  """
    Wrapper for Google Drive services related to file updates.
  """

  def __init__(self, drive_service):
    self.drive_service = drive_service

  #========================================================================
  # move_file
  #========================================================================

  @drive_file_id_operation("new_parent")
  def move_file(self, file, *, new_parent=None, new_name=None):
    """
      Move and/or rename the given file.  If new_parent is given, move the file to the
      new parent folder. If new_name is given, rename the file.
    """
    if not isinstance(file, DriveFile):
      raise ValueError("First parameter must be a DriveFile.")
    if new_parent is None and new_name is None:
      logger.warn("Either new parent or new name must be specified.")
      return

    update_args = {
        "fileId": file.id,
        "fields": DriveFile.FIELDS_SPEC,
        "supportsAllDrives": True,
    }

    if new_parent:
      logger.debug(f"Move file {file.name} ({file.id}) to folder {new_parent}.")

      # Validate new parent folder.
      self.validate_folder(new_parent)

      # Remove the file from its current parent folder(s), while adding the new parent.
      update_args.update({
          "addParents": new_parent,
          "removeParents": file.parent_id,
      })

    if new_name:
      logger.debug(f"Rename {file.id} to {new_name}.")
      update_args.update({
          "body": {
              "name": new_name
          },
      })

    with http_error_handling(f"Moving/renaming file {file.id}"):
      f = self.drive_service.files().update(**update_args).execute()
      return DriveFile(f)

  def validate_folder(self, folder):
    if not isinstance(folder, DriveFile):
      with http_error_handling(f"Validating folder {folder}"):
        f = self.drive_service.files().get(fileId=folder, fields=DriveFile.FIELDS_SPEC).execute()
        folder = DriveFile(f)
    if not folder.is_folder:
      raise ValueError("File {folder.id} ({folder.name}) is not a folder.")
    return folder

  #========================================================================
  # update_file_owner
  #========================================================================

  @drive_file_id_operation()
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

  #========================================================================
  # update_file_properties
  #========================================================================

  @drive_file_id_operation()
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
