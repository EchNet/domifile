# domifile/ingest/commands.py
import click, json, logging, re
from flask.cli import with_appcontext


def install_ingest_commands(app):

  from domifile.db.registry import DatabaseRegistry
  from domifile.ingest.helpers import DocumentHelper
  from domifile.ingest.service import IngestService
  from domifile.models import Document

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

    m = re.search(r"/file/d/([a-zA-Z0-9_-]+)", root_file_id)
    if m:
      root_file_id = m.group(1)

    ingest_service.ingest_drive_hierarchy(root_file_id)
    ingest_service.close()

  app.cli.add_command(ingest_drive_command)

  @click.command("examine-post-ingest")
  @click.argument("file_id")
  @with_appcontext
  def examine_post_ingest(file_id):
    """ Examine the outcome of ingesting a file. """
    configure_logging()

    m = re.search(r"/file/d/([a-zA-Z0-9_-]+)", file_id)
    if m:
      file_id = m.group(1)

    db_session = DatabaseRegistry.instance().session_for(Document)
    document_helper = DocumentHelper(db_session)
    document = document_helper.document_for_drive_file_id(file_id)
    if not document:
      raise FileNotFoundError(file_id)

    click.echo(json.dumps(document.to_dict()))

  app.cli.add_command(examine_post_ingest)
