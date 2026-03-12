# domifile/ingest/commands.py
import click
import os
from flask.cli import with_appcontext


def install_ingest_commands(app):

  from domifile.db import db_transaction
  from domifile.drive import DriveService
  from .extractor import TextExtractor
  from .chunker import chunk_text
  from .models import Document, Chunk

  DRIVE_FOLDER_ID = "1ZFgdI25w87_nWt0rELtjU51QMTpaBx0o"

  @click.command("run-ingest")
  @click.argument("drive_folder_ids", nargs=-1)
  @with_appcontext
  def run_ingest(drive_folder_ids):
    if not drive_folder_ids:
      drive_folder_ids = [DRIVE_FOLDER_ID]

    service = DriveService()

    for drive_folder_id in drive_folder_ids:
      click.echo(f"Listing {drive_folder_id}...")
      files = service.query().children_of(drive_folder_id).excluding_folders().list()
      click.echo(f"Found {len(files)} file(s)...")

      for f in files:
        click.echo(f"Downloading {f.name}...")
        tmp_name = f"/tmp/{f.name}"
        try:
          path = service.download_file(f.id, tmp_name)
          text = TextExtractor.extract(path, f.mime_type)
        except Exception as e:
          print(f"❌ Error: {e}", flush=True)
        os.remove(tmp_name)

        click.echo(f"Chunking {f.name}...")
        with db_transaction(Document) as db_session:
          doc = Document(drive_file_id=f.id, filename=f.name, text=text)
          db_session.add(doc)
          db_session.flush()
          chunks = chunk_text(text)
          for c in chunks:
            db_session.add(Chunk(document_id=doc.id, text=c))

  app.cli.add_command(run_ingest)
