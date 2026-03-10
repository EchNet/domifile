# domifile/drive/errors.py

import logging
from contextlib import contextmanager
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


class DriveFileNotFoundError(Exception):
  pass


class ApplicationError(Exception):
  pass


@contextmanager
def http_error_handling(details):
  try:
    logger.debug(f"START {details}")
    yield
    logger.debug(f"FINISH {details}")
  except HttpError as http_error:
    logger.error(f"Drive API error: {details} - {http_error}")
    error_code = http_error.resp.status
    if error_code == 404:
      raise DriveFileNotFoundError(f"ERROR: {details} - file not found") from http_error
    elif error_code in [401, 403]:
      raise PermissionError(f"ERROR: {details} - access denied") from http_error
    elif error_code < 500:
      raise ApplicationError(f"{details} - {http_error}") from http_error
    else:
      raise http_error
