import logging
from logging.handlers import RotatingFileHandler
import os

LOG_FILE = "debug.log"
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5 MB
BACKUP_COUNT = 3  # Keep last 3 log files


def define_logging(app):
  """ Set up application logging """

  # Configure root logger
  logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

  # Console Handler (INFO+)
  console_handler = logging.StreamHandler()
  console_handler.setLevel(logging.INFO)

  # File Handler (DEBUG+, with rollover)
  file_handler = RotatingFileHandler(LOG_FILE, maxBytes=MAX_LOG_SIZE, backupCount=BACKUP_COUNT)
  file_handler.setLevel(logging.DEBUG)
  file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

  # Attach handlers
  app.logger.addHandler(console_handler)
  app.logger.addHandler(file_handler)
