# Google Drive folder MIME type:
FOLDER_MIME_TYPE = "application/vnd.google-apps.folder"


class File:
  """ We prefer snakecase. """

  def __init__(self, drive_file_metadata):
    f = drive_file_metadata

    # Don't bother with supporting the outmoded practice of allowing multiple parents.
    parent_ids = f.get("parents", [])
    self.parent_id = parent_ids[0] if parent_ids else None

    # Owners is a list but shouldn't be.
    owners = f.get("owners", [])
    self.owner = owners[0]["emailAddress"] if owners else None
    print(self.owner)

    self.id = f.get("id")
    self.name = f.get("name")
    self.mime_type = f.get("mimeType")
    self.properties = f.get("properties") or {}

  @property
  def is_folder(self):
    return self.mime_type == FOLDER_MIME_TYPE
