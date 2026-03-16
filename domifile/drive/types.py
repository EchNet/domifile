# domifile/drive/types.py

from datetime import datetime


class DriveFile:
  """ Wrapper for a Google Drive file metadata dictionary. """

  # Google Drive folder MIME type:
  FOLDER_MIME_TYPE = "application/vnd.google-apps.folder"

  # All file metadata dictionaries are expected to have the following fields:
  FIELDS = (
      "id",
      "name",
      "mimeType",
      "parents",
      "properties",
      "owners",
      "trashed",
      "modifiedTime",
  )
  FIELDS_SPEC = ", ".join(FIELDS)

  def __init__(self, drive_file_metadata):
    f = drive_file_metadata

    # Don't bother with supporting the outmoded practice of allowing multiple parents.
    parent_ids = f.get("parents", [])
    self.parent_id = parent_ids[0] if parent_ids else None

    # Owners is a list but shouldn't be.
    self.owner = self._get_owner(f)

    self.id = f.get("id")
    self.name = f.get("name")
    self.mime_type = f.get("mimeType")
    self.properties = f.get("properties") or {}
    self.trashed = f.get("trashed") or False
    self.owner = self._get_owner(f)
    self.modified_time = datetime.fromisoformat(f.get("modifiedTime").replace("Z", "+00:00"))

  @staticmethod
  def _get_owner(f):
    owners = f.get("owners", [])
    if owners:
      owner = owners[0]
      for key in ["displayName", "emailAddress"]:
        if key in owner:
          return owner[key]
    return None

  @property
  def is_folder(self):
    return self.mime_type == self.FOLDER_MIME_TYPE
