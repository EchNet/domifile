# domifile/app/server.py
import logging, os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from werkzeug.exceptions import HTTPException


def configure_server(app):

  logger = logging.getLogger(__name__)

  # CORS
  CORS(app, supports_credentials=True, origins=app.config_obj.CORS_ALLOWED_ORIGINS)

  # Serve static front end assets.
  if app.config_obj.SERVE_STATIC:

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_static(path):
      full_path = os.path.join(app.static_folder, path)
      if not os.path.isfile(full_path):
        path = "index.html"
      return send_from_directory(app.static_folder, path)

  # Error responses are JSON.
  @app.errorhandler(HTTPException)
  def handle_http_exception(e):

    response = {
        "error": e.name.lower().replace(" ", "_"),
        "message": e.description,
        "status": e.code,
        "path": request.path,
    }
    return jsonify(response), e.code

  @app.errorhandler(Exception)
  def handle_exception(e):
    # Don't handle exceptions in testing mode.
    if app.testing:
      raise
    logger.exception("Unhandled exception at %s", request.path)
    # Unhandled / 500s
    response = {
        "error": "internal_server_error",
        "message": "An unexpected error occurred",
        "status": 500,
        "path": request.path,
    }
    return jsonify(response), 500
