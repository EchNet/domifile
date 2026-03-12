# domifile/db/Installer.py

# Install the DB registry.


class Installer:

  @classmethod
  def install(cls, app):
    """ Initialize DB registry and prepare it to accept installed components """

    from .registry import DatabaseRegistry

    DatabaseRegistry(app.config_obj)

    from .commands import install_db_commands

    install_db_commands(app)

  @classmethod
  def seal(cls):
    """ Ensure that DB registry accepts no more changes """

    from .registry import DatabaseRegistry

    DatabaseRegistry.instance().seal()
