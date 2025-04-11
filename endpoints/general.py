# endpoints/general.py


def define_general_endpoints(app):

  from flask import render_template, jsonify

  # Home page endpoint.
  @app.route("/", methods=['GET'])
  def index():
    return render_template("index.html")

  # Health check endpoint.
  @app.route('/status', methods=['POST'])
  def health_check():
    app.logger.debug("health check invoked")
    return jsonify({"status": "OK"}), 200
