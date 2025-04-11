# BucketManager.py

import logging
import os

from errors import ApplicationError
from managers.Bucket import Bucket
from managers.Classifier import Classifier
from models.Installation import Installation

logger = logging.getLogger(__name__)


class BucketManager:
  """
    Bucket actions.
  """

  def __init__(self, bucket_context):
    """
      Args
        context    A Bucket context.
    """
    self.bucket_context = bucket_context

  @property
  def installation(self):
    return self.bucket_context.installation

  @property
  def bucket(self):
    return self.bucket_context.bucket

  @property
  def drive_connector(self):
    return self.bucket_context.drive_connector

  def run_bucket_action(self):
    logger.info(f"run_bucket_action, bucket={self.bucket.name}")
    self.validate_bucket()
    self.validate_installation()
    action = self.bucket.properties.get(Bucket.BUCKET_ACTION_KEY)
    if action == Bucket.CLASSIFY_ACTION:
      return self.classify()
    elif action == Bucket.NO_ACTION or action is None:
      return None
    else:
      raise ApplicationError(f"Unknown action: {action}")

  def validate_bucket(self):
    pass

  def validate_installation(self):
    if self.installation.status != Installation.Status.IN_SERVICE:
      raise ApplicationError(
          f"Installation {self.installation.id} not in service ({self.installation.status}).")

  def classify(self):
    """
      Examine the contents of the inbox to find new files that require handling.
    """
    # List the contents of the inbox.
    files = self.drive_connector.query().children_of(self.bucket).list()
    for file in files:
      try:
        logger.info(f"classify file={file.name}")
        Classifier(self.bucket_context).classify_drive_file(file)
      except:
        logger.exception("Unexpected error")
        return  # TEMP
