from flask import Flask

import config
from commands import define_commands
from endpoints import define_endpoints
from google_auth import define_google_auth
from log import configure_root_logging
from managers import define_app_resources


def create_app(config_name, config_override=None):
  app = Flask(__name__)

  # Load config class by name.
  app.config.from_object(getattr(config, config_name))

  if config_override:
    app.config.update(config_override)

  from db import db
  db.init_app(app)

  verbose = bool(app.config.get("VERBOSE"))
  configure_root_logging(verbose)
  define_google_auth(app)
  define_endpoints(app)
  define_commands(app)
  define_app_resources(app)
  app.invoke_shared_task = invoke_shared_task
  return app


def invoke_shared_task(app, func, args):
  if app.config.get("USE_CELERY", False):
    func.delay(*args)
  else:
    func(*args)
