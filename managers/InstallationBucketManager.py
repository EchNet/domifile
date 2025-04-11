# InstallationBucketManager.py

import logging
from datetime import date

from db import db
from errors import ApplicationError
from managers.Bucket import Bucket

logger = logging.getLogger(__name__)


class InstallationBucketManager:
  """
    Create and list buckets for a given Installation.

    A bucket is a folder with a name that connotes its contents.  Buckets
    often have business rules that dictate the actions taken by the system
    when a file is added to the bucket or removed from it.  A bucket belongs
    to an installation.
  """

  def __init__(self, context):
    """
      Args
        context    An Installation context.
    """
    self.installation = context.installation
    self.root_folder_id = self.installation.root_folder_id
    self.drive_connector = context.drive_connector

  def create_bucket(self, name, *, action=Bucket.NO_ACTION, rename_existing=False):
    """
      Create a bucket as a child of the root folder.

      Parameters:
        name               The bucket name
        action             
        rename_existing
    """

    if not name:
      raise ApplicationError("Name may not be empty.")
    if "/" in name:
      raise ApplicationError("Name may not contain slashes (/).")
    if action not in Bucket.ACTIONS:
      raise ApplicationError(f"\"{action}\" is not a valid action.")

    # Check for existing file with that name.
    existing_file = self.drive_connector.query().children_of(
        self.root_folder_id).named(name).first()

    folder = None

    if existing_file:
      if existing_file.is_folder:
        logger.info(f"Reusing existing folder \"{name}\".")
        folder = existing_file
        self.drive_connector.update_file_properties(folder, {Bucket.BUCKET_ACTION_KEY: action})
      elif rename_existing:
        today = date.today().strftime("%Y-%m-%d")
        new_name = f"{name}-{today}"
        logger.info('Renaming existing file "{name}" to "{new_name}".')
        self.drive_connector.rename_file(existing_file, new_name)
      else:
        raise ApplicationError(f"There is already a file named \"{name}\".")

    if not folder:
      logger.info(f"Creating new folder \"{name}\".")
      folder = self.drive_connector.create_folder(name,
                                                  parent=self.root_folder_id,
                                                  properties={Bucket.BUCKET_ACTION_KEY: action})
    self.installation.last_refresh = None
    db.session.commit()

  def list_buckets(self):
    """
      List buckets in current installation.
    """
    return self.drive_connector.query().children_of(
        self.root_folder_id).only_folders().having_property(Bucket.BUCKET_ACTION_KEY).list()
