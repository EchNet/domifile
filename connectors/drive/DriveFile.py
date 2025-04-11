# DriveFile.py

import json


class DriveFile:
  """ Wrapper for a Google Drive file metadata dictionary. """

  # Google Drive folder MIME type:
  FOLDER_MIME_TYPE = "application/vnd.google-apps.folder"

  # All file metadata dictionaries are expected to have the following fields:
  FIELDS = ("id", "name", "mimeType", "parents", "properties", "owners", "trashed")
  FIELDS_SPEC = ", ".join(FIELDS)

  def __init__(self, drive_file_metadata):
    f = drive_file_metadata

    # Don't bother with supporting the outmoded practice of allowing multiple parents.
    parent_ids = f.get("parents", [])
    self.parent_id = parent_ids[0] if parent_ids else None

    # Owners is a list but shouldn't be.
    owners = f.get("owners", [])
    self.owner = owners[0]["emailAddress"] if owners else None

    self.id = f.get("id")
    self.name = f.get("name")
    self.mime_type = f.get("mimeType")
    self.properties = f.get("properties") or {}
    self.trashed = f.get("trashed") or False

  @property
  def is_folder(self):
    return self.mime_type == self.FOLDER_MIME_TYPE

  def dict(self):
    return {
        "id": self.id,
        "name": self.name,
        "mime_type": self.mime_type,
        "properties": self.properties,
        "parent_id": self.parent_id,
        "owner": self.owner,
        "trashed": self.trashed,
    }

  def __str__(self):
    return json.dumps(self.dict())
