# domifile/ingest/commands.py

import click
import logging
from flask.cli import with_appcontext


def install_ingest_commands(app):

  from domifile.ingest.service import IngestService

  class DebugModuleFilter(logging.Filter):

    def __init__(self, modules):
      super().__init__()
      self.modules = modules

    def filter(self, record):
      # allow DEBUG only for selected modules
      if record.levelno >= logging.WARNING:
        return True
      if record.levelno >= logging.DEBUG:
        return any(record.name.startswith(m) for m in self.modules)
      return False

  def configure_logging():
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)  # accept everything, filter decides

    handler.addFilter(DebugModuleFilter([
        "domifile.ingest",
    ]))

    formatter = logging.Formatter("%(levelname)s - %(name)s - %(message)s")
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.handlers = [handler]

    logging.getLogger("pdfminer").setLevel(logging.ERROR)

  @click.command("ingest-drive")
  @click.argument("root_file_id")
  @with_appcontext
  def ingest_drive_command(root_file_id):
    """Traverse a Google Drive folder/file hierarchy and ingest all contents."""
    configure_logging()
    ingest_service = IngestService()
    ingest_service.ingest_drive_hierarchy(root_file_id)
    ingest_service.close()

  app.cli.add_command(ingest_drive_command)
