# domifile/ingest/commands.py
import click, json, logging, re
from flask.cli import with_appcontext


def install_ingest_commands(app):
  from domifile.ingest.helpers import DocumentFinder
  from domifile.ingest.service import IngestService

  def normalize_file_id(file_id):
    patterns = [
        r"/file/d/([a-zA-Z0-9_-]+)",
        r"/folders/([a-zA-Z0-9_-]+)",
        r"[?&]id=([a-zA-Z0-9_-]+)",
    ]
    for p in patterns:
      m = re.search(p, file_id)
      if m:
        return m.group(1)
    return file_id

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

    root_file_id = normalize_file_id(root_file_id)

    output = IngestService().ingest_drive_hierarchy(root_file_id)
    click.echo(json.dumps(output))
    ingest_service.close()

  app.cli.add_command(ingest_drive_command)

  @click.command("examine-drive-file")
  @click.argument("file_id")
  @with_appcontext
  def examine_drive_file(file_id):
    """ Examine the outcome of ingesting a file. """
    configure_logging()

    file_id = normalize_file_id(file_id)
    db_session = create_db_session()
    document = DocumentFinder(db_session=db_session).document_for_drive_file_id(file_id)
    if not document:
      click.echo(f"No info for {file_id}")
    else:
      click.echo(json.dumps(document.to_dict(), indent=2))

  app.cli.add_command(examine_drive_file)

  @click.command("clear-ingest-drive")
  @click.argument("root_file_id")
  @with_appcontext
  def clear_ingest_drive(root_file_id):
    """Traverse a Google Drive folder/file hierarchy and clear all ingested content."""
    configure_logging()
    ingest_service = IngestService(db_session=create_db_session())
    root_file_id = normalize_file_id(root_file_id)
    count = ingest_service.clear_drive_hierarchy(root_file_id)
    click.echo(f"Done. Cleared {count}.")
    ingest_service.close()

  app.cli.add_command(clear_ingest_drive)
