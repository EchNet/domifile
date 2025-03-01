# installation_manager.py
#
# Manage the continuance or termination of the service for its various installations.
#
# See to it that for each active installation, its folder structure has been created
# and there is a watcher on it.
#
# Every installation marked for termination will be terminated.
#
from connectors.drive_connector import DriveConnector, DriveFileNotFoundError
from datetime import datetime, timezone, timedelta
import dateutil
from environment import ServiceAccountInfo
from managers.inbox_file_manager import InboxFileManager
from models.installation import Installation
import os


class InstallationManager:
  """
    InstallationManager is responsible for one installation.
  """

  def __init__(self, installation):
    """
      Constructor

      Parameters
        installation     A current Installation model object
    """
    self.installation = installation
    self.root_folder_id = self.installation.root_folder_id

    # Build a Google Drive service using the credentials provided by the creator of the
    # installation.
    self.drive_service = DriveConnector(
        ServiceAccountInfo.from_json_string(self.installation.service_account_info))

    # Validate root folder.
    root_folder = self.drive_service.get(self.root_folder_id)
    if not root_folder:
      raise ValueError(f"{root_folder_id}: no such folder")
    if not root_folder.is_folder:
      raise ValueError(f"{root_folder_id}: is not a folder")

    DESTINATION_FOLDERS = ["Minutes", "Proposals", "Notices", "Invoices", "Receipts"]

    def folder_of_name(folder_name):
      folder = self.drive_service.query().children_of(
          self.root_folder_id).named(folder_name).only_folders().get()
      if folder is None:
        print(f"Creating folder {folder_name}")
        folder = self.drive_service.create_folder(folder_name, self.root_folder_id,
                                                  root_folder.owner)
      return folder.id

    # Find and create folders for sorting documents.
    self.inbox_id = folder_of_name("INBOX")
    self.system_folder_id = folder_of_name("SYSTEM")  # TODO: make non-writeable
    self.destination_folders = {
        folder_name: folder_of_name(folder_name)
        for folder_name in DESTINATION_FOLDERS
    }

  def update_watcher(self):
    """
      Start, continue or terminate this installation's watcher as appropriate.
    """
    webhook_url = os.getenv("WEBHOOK_URL")
    if not webhook_url:
      raise ValueError("Environment variable WEBHOOK_URL must be set")

    ##########################################
    # Inner functions
    ##########################################

    def get_channel_id():
      return f"domi-{self.installation.id}"

    def start_watcher():
      """
        Set up a Google Drive watch on the inbox.
      """
      return self.drive_service.create_watch_channel(channel_id=get_channel_id(),
                                                     file_id=self.inbox_id,
                                                     webhook_url=webhook_url)

    def refresh_watcher():
      cancel_watcher()
      return start_watcher()

    def cancel_watcher():
      if self.installation.inbox_watcher_resource_id:
        print(f"Canceling watcher on {self.inbox_id}")
        self.drive_service.close_watch_channel(
            channel_id=get_channel_id(), resource_id=self.installation.inbox_watcher_resource_id)
      else:
        print(f"No watcher resource ID on {self.inbox_id}... ignoring.")

    def refresh_required():
      last_refresh = self.installation.last_refresh
      return not last_refresh or datetime.now(timezone.utc) - last_refesh > timedelta(days=1)

    def advance():
      """ If the Installation is ready for transition, execute the transition. """

      # If installation is READY, put it into service.
      if self.installation.status == Installation.Status.READY:
        print(f"Starting up service installation={self.installation.id}")
        inbox_watcher_resource_id = start_watcher()
        return {
            "inbox_watcher_resource_id": inbox_watcher_resource_id,
            "status": Installation.Status.IN_SERVICE
        }

      # If installation is in service but the watcher has not been refreshed in
      # over a day, refresh it.
      if self.installation.status == Installation.Status.IN_SERVICE:
        if refresh_required():
          print(f"Refreshing service installation={self.installation.id}")
          try:
            inbox_watcher_resource_id = refresh_watcher()
          except Exception as e:
            print("ERROR: {e}")
            return {"status": Installation.Status.BLOCKED}
          return {"inbox_watcher_resource_id": inbox_watcher_resource_id}

      # If installation is marked for termination, terminate it.
      if self.installation.status == Installation.Status.MARKED_FOR_TERMINATION:
        print(f"Terminating service installation={self.installation.id}")
        try:
          cancel_watcher()
        except Exception as e:
          print("WARNING: {e}")
        return {"inbox_watcher_resource_id": "", "status": Installation.Status.TERMINATED}

    ##########################################
    # END Inner functions
    ##########################################

    updates = advance()
    if updates:
      updates.update({"last_refresh": datetime.utcnow()})
      self.installation.update(updates)

  def run_inbox_worker(self):
    """
      Examine the contents of the inbox to find new files that require handling.
    """
    # List the contents of the inbox.
    files = self.drive_service.query().children_of(self.inbox_id).list()
    for file in files:

      # Check if the property 'initiated_at' is present
      initiated_at = file.properties.get("initiated_at")
      if initiated_at:
        try:
          # Parse the date as timezone-aware
          initiated_datetime = dateutil.parser.isoparse(initiated_at)
          initiated_datetime = initiated_datetime.astimezone(timezone.utc)
          # Get current time in UTC
          now = datetime.now(timezone.utc)
          # Check if it is less than one hour in the past
          if now - initiated_datetime <= timedelta(hours=1):
            # Skip file.
            continue
        except Exception as e:
          print(f"Error: file={file.name} {e}")

        now = datetime.now(timezone.utc).isoformat()
        self.drive_service.set_file_metadata(file.id, {"initiated_at": now})

        try:
          InboxFileManager(self, file).process_inbox_file()
        except Exception as e:
          print(f"Error: file={file.name} {e}")
