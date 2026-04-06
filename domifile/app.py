# domifile/__init__.py
import importlib
import logging
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

  def install_db(self):
    from domifile.db import DatabaseRegistry
    from .models import Base

    # Initialize DB registry
    db_registry = DatabaseRegistry(self.app.config_obj)
    db_registry.bind(Base, self.app.config_obj.DATABASE_URL)
    db_registry.seal()

    return self

  # --------------------------------------------------------------------------------

  def install_blueprint(self):

    from .blueprint import install_blueprint

    install_blueprint(self.app)

    return self

  # --------------------------------------------------------------------------------

  def install_cli(self):

    from .db.commands import install_db_commands
    from .ingest.commands import install_ingest_commands
    from .query.commands import install_query_commands
    from .cli import patch_cli

    install_db_commands(self.app)
    install_ingest_commands(self.app)
    install_query_commands(self.app)
    patch_cli(self.app)

    return self


# ------------------------------------------------------------------
# Main entry point
# ------------------------------------------------------------------


def create_app():
  return AppBuilder() \
    .configure_logging() \
    .configure_server() \
    .install_db() \
    .install_blueprint() \
    .install_cli() \
    .app
