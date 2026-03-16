# domifile/ingest/commands.py
import click
from flask.cli import with_appcontext

from .ingester import Ingester


def install_ingest_commands(app):

  DRIVE_FOLDER_ID = "1ZFgdI25w87_nWt0rELtjU51QMTpaBx0o"

  @click.command("run-ingest")
  @click.argument("drive_folder_ids", nargs=-1)
  @with_appcontext
  def run_ingest(drive_folder_ids):
    if not drive_folder_ids:
      drive_folder_ids = [DRIVE_FOLDER_ID]

    try:
      for dfi in drive_folder_ids:
        Ingester().ingest_from_drive(dfi)
    except Exception as e:
      print(f"❌ Error: {e}", flush=True)

  app.cli.add_command(run_ingest)
