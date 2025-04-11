# actions/tasks.py

from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task
def take_action_on_change_to_watched_folder(installation_id, folder_id):

  logger.info(f"action: installation_id={installation_id}")

  try:
    installation = Installation.query.get(installation_id)
    if not installation:
      app.logger.error(f"Installation {installation_id} not found.")
    elif installation.status != Installation.Status.IN_SERVICE:
      app.logger.error(f"Installation {installation_id} not in service ({installation.status}).")
    else:
      installation = Installation.query.get(installation_id)
      InstallationManager(installation).run_inbox_worker()
  except Exception as e:
    logger.exception(e)

  context = AppContext()
  context = InstallationContext(context, installation_id)
  context = FileContext(context, file_id)
