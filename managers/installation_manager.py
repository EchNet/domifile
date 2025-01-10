# installation_manager.py
#
# Manage the continuance or termination of the service for its various installations.
#
# See to it that for each active installation, its folder structure has been created
# and there is a watcher on it.
#
# Every installation marked for termination will be terminated.
#
from connectors.drive_connector import DriveService
from environment import ServiceAccountInfo
from managers.inbox_file_manager import InboxFileManager
from models import Installation


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
    self.drive_service = DriveService(
        ServiceAccountInfo.from_json_string(self.installation.service_account_info))

    DESTINATION_FOLDERS = ["Minutes", "Proposals", "Notices", "Invoices", "Receipts", "2025"]

    def folder_of_name(folder_name):
      # TODO: handle trashed inbox
      folder = self.drive_service.query().children_of(
          self.root_folder_id).named(folder_name).only_folders().get()
      if folder is None:
        print(f"Creating folder {folder_name}")
        folder = self.drive_service.create_folder(folder_name, self.root_folder_id)
      return folder["id"]

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
    WEBHOOK_URL = "https://hostname/webhook"

    installation = self.installation

    def start_watcher():
      """
        Set up a Google Drive watch on the inbox.
      """
      return self.drive_service.watch_resource(source_file_id=self.inbox_id,
                                               webhook_url=WEBHOOK_URL)

    def refresh_watcher():
      cancel_watcher()
      return start_watcher()

    def cancel_watcher():
      if installation.inbox_watcher_resource_id:
        print(f"Canceling watcher on {self.inbox_id}")
        self.drive_service.unwatch_resource(source_file_id=self.inbox_id,
                                            resource_id=installation.inbox_watcher_resource_id)
      else:
        print(f"No watcher resource ID on {self.inbox_id}... ignoring.")

    try:
      if installation.status == Installation.Status.READY:
        print("Starting up installation {installation.id}")
        inbox_watcher_resource_id = start_watcher()
        installation.update(
            dict(status=Installation.Status.IN_SERVICE,
                 inbox_watcher_resource_id=inbox_watcher_resource_id,
                 last_refresh=True))
      elif installation.status == Installation.Status.IN_SERVICE:
        print(f"Continuing installation {installation.id}")
        inbox_watcher_resource_id = refresh_watcher()
        installation.update(
            dict(inbox_watcher_resource_id=inbox_watcher_resource_id, last_refresh=True))
      elif installation.status == Installation.Status.MARKED_FOR_TERMINATION:
        print(f"Terminating installation {installation.id}")
        cancel_watcher()
        installation.update(
            dict(status=Installation.Status.TERMINATED, inbox_watcher_resource_id=""))
    except Exception as e:
      installation.update(dict(status=Installation.Status.BLOCKED))
      raise Exception(f"Unable to update watcher on INBOX") from e

  def run_inbox_worker(self, resource_id=None):
    """
      Examine the contents of the inbox to find new files that require
      organization.
    """
    if resource_id is not None and self.inbox_id != resource_id:
      print("WARNING: inbox has moved")

    # Get the contents of the inbox.  Ignore folders for now.
    files = self.drive_service.query().children_of(self.inbox_id).excluding_folders().list()
    for file in files:
      try:
        InboxFileManager(self, file).process_inbox_file()
      except Exception as e:
        raise Exception(f"Unable to organize files in INBOX") from e
