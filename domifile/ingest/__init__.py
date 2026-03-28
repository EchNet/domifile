# domifile/ingest/__init__.py


def install_ingest(app):

  from .commands import ingest_drive_command

  app.cli.add_command(ingest_drive_command)
