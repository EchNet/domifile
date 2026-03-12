# domifile/ingest/Installer.py

# Register ingest database and commands


class Installer:

  @classmethod
  def install(cls, app):
    """ Initialize DB registry and prepare it to accept installed components """

    from domifile.db.registry import DatabaseRegistry
    from .models import Base

    DatabaseRegistry.instance().bind(Base, app.config_obj.DATABASE_URL)

    from .commands import install_ingest_commands

    install_ingest_commands(app)
