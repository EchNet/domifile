# tasks/bucket_tasks.py

import logging
from celery import shared_task
from flask import current_app

from managers.BucketManager import BucketManager

logger = logging.getLogger(__name__)


@shared_task
def run_bucket_action(installation_id, folder_id):
  """ Respond to a push notification of change to a watched folder. """

  logger.info(f"START bucket action: installation_id={installation_id} folder_id={folder_id}")

  def log_action_summary(self, summary):
    # TODO:
    logger.info(summary)

  def log_authorization_error(self, e):
    # TODO
    logger.error(e)

  def log_application_error(self, e):
    # TODO
    logger.error(e)

  def log_unexpected_error(self, e):
    # TODO: alert admins
    logger.error(e)

  try:
    context = current_app.create_bucket_context(installation_id=installation_id,
                                                folder_id=folder_id)
    summary = BucketManager(context).execute_action()
    log_action_summary(summary)
  except AuthorizationError as e:
    log_authorization_error(e)
  except ApplicationError as e:
    log_application_error(e)
  except Exception as e:
    log_unexpected_error(e)

  logger.info(f"END bucket action: installation_id={installation_id} folder_id={folder_id}")
