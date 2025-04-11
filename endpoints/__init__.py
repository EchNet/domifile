# endpoints/__init__.py

import logging

from endpoints.general import define_general_endpoints
from endpoints.install import define_install_endpoints
from endpoints.webhook import define_webhook_endpoints

logger = logging.getLogger(__name__)


def define_endpoints(app):
  """ Define service endpoints. """

  from flask import request

  @app.before_request
  def log_request():
    logger.debug(f"Request: {request.method}, {request.url}")
    logger.debug(f"Request headers: {request.headers}")

  define_general_endpoints(app)
  define_install_endpoints(app)
  define_webhook_endpoints(app)
