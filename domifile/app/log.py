# domifile/app/log.py
import os

LOG_FILE = "debug.log"
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5 MB
BACKUP_COUNT = 3


def configure_root_logging(verbose=False):
  import logging
  from logging.handlers import RotatingFileHandler

  formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

  run_from_cli = os.getenv("FLASK_RUN_FROM_CLI") == "true"
  log_level = logging.DEBUG if verbose else logging.WARN if run_from_cli else logging.INFO

  # Console handler
  console_handler = logging.StreamHandler()
  console_handler.setLevel(log_level)
  console_handler.setFormatter(formatter)

  # File handler
  file_handler = RotatingFileHandler(LOG_FILE, maxBytes=MAX_LOG_SIZE, backupCount=BACKUP_COUNT)
  file_handler.setLevel(logging.DEBUG)
  file_handler.setFormatter(formatter)

  # Configure root logger
  root_logger = logging.getLogger()
  root_logger.setLevel(logging.DEBUG)
  root_logger.propagate = False
  if root_logger.hasHandlers():
    root_logger.handlers.clear()
  root_logger.addHandler(console_handler)
  root_logger.addHandler(file_handler)

  # =======================================
  # Tell overactive loggers to be quiet.
  # =======================================

  logging.getLogger("werkzeug").setLevel(logging.WARNING)
  logging.getLogger("httpx").setLevel(logging.WARNING)
  logging.getLogger("httpcore").setLevel(logging.WARNING)
