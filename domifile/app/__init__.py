# domifile/app/__init__.py
import importlib
import os
from flask import Flask
from os import path


class AppBuilder:

  def __init__(self):
    """ Construct Flask app and load its configuration """

    project_root = path.abspath(path.join(path.dirname(__file__), '..'))

    static_folder = path.join(project_root, "static")

    self.app = Flask(__name__, static_folder=static_folder, static_url_path="")

    from .config import get_app_config

    # Load the configuration object specified by env APP_CONFIG
    app_config = get_app_config()
    self.config = app_config
    self.app.config.from_object(app_config)
    self.app.config_obj = app_config  # Make the typed object accessible.

    self.app.components = {}

  # --------------------------------------------------------------------------------

  def configure_logging(self):
    """ Configure application-wide logging """

    from .log import configure_root_logging

    configure_root_logging(verbose=bool(self.config.VERBOSE))

    return self

  # --------------------------------------------------------------------------------

  def configure_server(self):
    """ Configure web server """

    from .server import configure_server

    configure_server(self.app)

    return self

  # --------------------------------------------------------------------------------

  def init_socketio(self):
    """ Initialize the socket server if running in full server mode. """

    # Don't initialize socketio for CLI commands.
    if not "FLASK_RUN_FROM_CLI" in os.environ:

      from .socketio import install_socketio

      install_socketio(self.app)

    return self

  # --------------------------------------------------------------------------------

  @property
  def installers(self):
    """
      Iterate over the platform and application components in dependency order 
      Yield an `Installer` class from each module name provided.
    """
    module_names = (
        "domifile.db",
        "domifile.ingest",
    )

    for module_name in module_names:
      module = importlib.import_module(module_name)
      try:
        installer_cls = getattr(module, "Installer")
      except AttributeError:
        raise ImportError(f"{module_name} does not define Installer")

      yield installer_cls, module_name

  def install_components(self, last_installer=None):
    import logging

    logger = logging.getLogger("app_init")
    logger.debug("INSTALL COMPONENTS")

    for installer, module_name in self.installers:
      if hasattr(installer, "install"):
        logger.debug(f"Installing {module_name}")
        installer.install(self.app)
      if installer == last_installer:
        logger.debug(f"Breaking after installing {module_name}")
        break

    for installer, module_name in self.installers:
      if hasattr(installer, "seal"):
        logger.debug(f"Sealing {module_name}")
        installer.seal()
      if installer == last_installer:
        logger.debug(f"Breaking after sealing {module_name}")
        break

    return self

  # --------------------------------------------------------------------------------

  def patch_cli(self):
    """ Post-process the installed CLI commands """

    from .cli import patch_cli_commands

    patch_cli_commands(self.app)

    return self


# ------------------------------------------------------------------
# Main entry point
# ------------------------------------------------------------------


def create_app(*, last_installer=None):
  return AppBuilder() \
    .configure_logging() \
    .configure_server() \
    .init_socketio() \
    .install_components(last_installer) \
    .patch_cli() \
    .app
