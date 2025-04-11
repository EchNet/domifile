# installation_manager.py
#
# Manage the continuance or termination of the service for its various installations.
#
# See to it that for each active installation, its folder structure has been created
# and there is a watcher on it.
#
# Every installation marked for termination will be terminated.
#
# TODO:
# The inbox is not the only watchable folder per installation.  Extend the approach
# allow for multiple watched folders.
#
# Drop the inbox_resource_id field of Installation.
# Store the resource ID in the properties of the folder.
# Refresh all watches periodically.
#
from datetime import datetime, timezone, timedelta, UTC
import dateutil
import os

from connectors.drive.DriveConnector import DriveConnector
from connectors.drive.errors import DriveFileNotFoundError
from models.Installation import Installation

NO_ACTION = "none"
VALID_ACTIONS = [
    NO_ACTION,
    "broadcast",
    "classify",
    "register-invoice",
]
BUCKET_ACTION_KEY = "--dof-action"


def is_bucket(file):
  return file.is_folder and BUCKET_ACTION_KEY in file.properties


class InstallationManager:
  """
    InstallationManager is responsible for one installation.
  """

  def __init__(self, context):
    self.installation = context.installation
    self.root_folder_id = self.installation.root_folder_id
    self.drive_connector = context.drive_connector

  def apply_template(self):
    """ For example, the HOA template. """
    pass

  def create_bucket(self, name, action=NO_ACTION):
    existing_file = self.drive_connector.query().children_of(
        self.root_folder_id).named(name).first()
    if existing_file:
      what = ("bucket"
              if is_bucket(existing_file) else "folder" if existing_file.is_folder else "file")
      raise Exception(f"There is already a {what} of that name.")
    if action not in VALID_ACTIONS:
      raise Exception(f"\"{action}\" is not a valid action.")
    self.drive_connector.create_folder(name,
                                       parent=self.root_folder_id,
                                       properties={BUCKET_ACTION_KEY: action})

  def update_watchers(self):
    """
      Start, continue or terminate this installation's watchers as appropriate.
    """
    webhook_url = os.getenv("WEBHOOK_URL")
    if not webhook_url:
      raise ValueError("Environment variable WEBHOOK_URL must be set")

    ##########################################
    # Inner functions
    ##########################################

    def get_channel_id(folder_id):
      return f"--dof-{self.installation.id}-{folder_id}"

    def start_watcher(folder_id):
      """
        Set up a Google Drive watch on the inbox.
      """
      return self.drive_connector.create_watch_channel(channel_id=get_channel_id(),
                                                       file_id=folder_id,
                                                       webhook_url=webhook_url)

    def refresh_watcher(folder_id):
      cancel_watcher(folder_id)
      return start_watcher(folder_id)

    def cancel_watcher(folder_id):
      if self.installation.inbox_watcher_resource_id:
        print(f"Canceling watcher on {self.inbox_id}")
        self.drive_connector.close_watch_channel(
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
        for subfolder in (self.drive_connector.query().children_of(
            self.installation.root_folder_id).only_folders().list()):
          if subfolder.properties.get("--dof-action"):
            start_watcher(subfolder)
        return {"status": Installation.Status.IN_SERVICE}

      # If installation is in service but the watcher has not been refreshed in
      # over a day, refresh it.
      if self.installation.status == Installation.Status.IN_SERVICE:
        if refresh_required():
          print(f"Refreshing service installation={self.installation.id}")
          try:
            for subfolder in (self.drive_connector.query().children_of(
                installation.root_folder_id).only_folders().list()):
              if subfolder.properties.get("--dof-action"):
                refresh_watcher(subfolder)
          except Exception as e:
            print("ERROR: {e}")
            return {"status": Installation.Status.BLOCKED}
          return {"inbox_watcher_resource_id": inbox_watcher_resource_id}

      # If installation is marked for termination, terminate it.
      if self.installation.status == Installation.Status.MARKED_FOR_TERMINATION:
        print(f"Terminating service installation={self.installation.id}")
        try:
          for subfolder in (self.drive_connector.query().children_of(
              installation.root_folder_id).only_folders().list()):
            if subfolder.properties.get("--dof-watcher"):
              cancel_watcher(subfolder)
        except Exception as e:
          print("WARNING: {e}")
        return {"inbox_watcher_resource_id": "", "status": Installation.Status.TERMINATED}

    ##########################################
    # END Inner functions
    ##########################################

    updates = advance()
    if updates:
      updates.update({"last_refresh": datetime.now(UTC)})
      self.installation.update(updates)

  def run_inbox_worker(self):
    """
      Examine the contents of the inbox to find new files that require handling.
    """
    # List the contents of the inbox.
    files = self.drive_connector.query().children_of(self.inbox_id).list()
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
        self.drive_connector.update_file_properties(file.id, {"initiated_at": now})

        # Now, run the action specified in the folder properties.
