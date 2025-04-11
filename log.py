import logging
from logging.handlers import RotatingFileHandler

LOG_FILE = "debug.log"
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5 MB
BACKUP_COUNT = 3


def configure_root_logging(verbose=False):
  log_level = logging.DEBUG if verbose else logging.INFO
  formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

  # Create handlers
  console_handler = logging.StreamHandler()
  console_handler.setLevel(log_level)
  console_handler.setFormatter(formatter)

  file_handler = RotatingFileHandler(LOG_FILE, maxBytes=MAX_LOG_SIZE, backupCount=BACKUP_COUNT)
  file_handler.setLevel(logging.DEBUG)
  file_handler.setFormatter(formatter)

  # Clear existing handlers from root logger
  root_logger = logging.getLogger()
  root_logger.setLevel(log_level)
  if root_logger.hasHandlers():
    root_logger.handlers.clear()

  root_logger.addHandler(console_handler)
  root_logger.addHandler(file_handler)
