

class InstallationDriveManager:

  def __init__(self, context)
    self.context = context

  @property
  def root_folder_id(self):
    return self.installation.root_folder_id

  @property
  def root_folder(self):
    root_folder = DriveConnector(self.context.drive_service).get(self.root_folder_id)
    if not root_folder:
      raise ValueError(f"{root_folder_id}: no such folder")
    if not root_folder.is_folder:
      raise ValueError(f"{root_folder_id}: is not a folder")
