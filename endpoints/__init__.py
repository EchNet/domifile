# endpoints/__init__.py

from endpoints.general import define_general_endpoints
from endpoints.install import define_install_endpoints
from endpoints.webhook import define_webhook_endpoints


def define_endpoints(app):
  """ Define service endpoints. """

  from flask import request

  @app.before_request
  def log_request():
    app.logger.debug(f"Request: {request.method}, {request.url}")
    app.logger.debug(f"Request headers: {request.headers}")

  define_general_endpoints(app)
  define_install_endpoints(app)
  define_webhook_endpoints(app)
