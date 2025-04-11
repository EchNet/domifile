# service_manager.py
#
# Manage the continuance or termination of the service for its various installations.
#

import logging
from datetime import datetime, timedelta, UTC
from flask import current_app

from connectors.drive.errors import DriveFileNotFoundError
from db import db
from managers.InstallationManager import InstallationManager
from models.Installation import Installation

logger = logging.getLogger(__name__)


class ServiceManager:
  """
    ServiceManager is responsible for maintaining the service as a whole.
  """
  REFRESH_DAYS = 3

  @classmethod
  def create_installation(cls, creator, root_folder_id, service_account_filename):
    context = current_app.create_ad_hoc_context(
        service_account_json_path=service_account_filename)
    service_account_json = context.service_account_json

    # Validate input values.
    values = Installation.validate_installation_values({
        "creator":
        creator,
        "root_folder_id":
        root_folder_id,
        "service_account_info":
        service_account_json
    })

    # Validate access to root folder.
    try:
      folder = context.drive_connector.get(root_folder_id)
      if not folder.is_folder:
        raise Exception(f"Specified root folder {root_folder_id} is not a folder.")
    except DriveFileNotFoundError as e:
      raise Exception(
          f"Root folder {root_folder_id} not found or not visible to service account.")
    context.drive_connector.update_file_properties(root_folder_id, {"--omn-action": "root"})

    # Check for existing installation for this root folder.
    installation = Installation.get_by_root_folder_id(root_folder_id)
    if installation:
      # Already exists. Reuse the Installation object.  This means that if the installation is
      # marked for termination, push it back into "in service" state, so that its watcher is
      # refreshed.
      print(f"Reusing Installation object {installation}")
      if installation.status in (Installation.Status.MARKED_FOR_TERMINATION,
                                 Installation.Status.TERMINATED, Installation.Status.BLOCKED):
        installation.status = Installation.Status.IN_SERVICE
      installation.creator = values["creator"]
      installation.service_account_info = values["service_account_info"]
    else:
      # Create new Installation.
      print("Creating new Installation object")
      installation = Installation.create(values)

    context = current_app.create_installation_context(installation=installation)

    # TODO: delegate this to a task.  Add Installation.status to track errors.
    try:
      # Create / cancel and recreate all watchers.
      InstallationManager(context).update_watchers()
    except:
      logger.exception(f"Unable to update watchers on installation #{installation.id}.")

    return installation

  @classmethod
  def maintain_service(cls):
    """
      See to it that for each active installation, its minimal folder structure has
      been created and there is a watcher on it.
    """
    three_days_ago = datetime.now(UTC) - timedelta(days=cls.REFRESH_DAYS)

    installations = Installation.query.filter(
        # Exclude TERMINATED...
        Installation.status != Installation.Status.TERMINATED,
        # Exclude recently refreshed...
        ~((Installation.status == Installation.Status.IN_SERVICE) &
          (Installation.last_refresh >= three_days_ago))).all()

    for installation in installations:
      InstallationManager(installation).update_watcher()

  @classmethod
  def terminate_service(cls):

    installations = Installation.query.all()
    for installation in installations:
      print(
          f"{installation.id} {installation.creator} {installation.root_folder_id} {installation.status}"
      )
      if installation.status == Installation.Status.READY:
        installation.update(dict(status=Installation.Status.TERMINATED))
      elif installation.status == Installation.Status.IN_SERVICE:
        installation.update(dict(status=Installation.Status.MARKED_FOR_TERMINATION))
      # Close watchers as needed.
      InstallationManager(installation).update_watcher()

    db.session.query(Installation).delete()
    db.session.commit()
