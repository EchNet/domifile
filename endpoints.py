# endpoints.py
#
# App endpoints.
#
# Includes API methods for creating, retrieving and terminating installations.
#


def define_endpoints(app):

  from auth import auth_required
  from flask import abort, render_template, request, jsonify
  from flask import session
  from flask_dance.contrib.google import google
  from managers.installation_manager import InstallationManager
  from models.installation import Installation

  @app.before_request
  def log_request():
    app.logger.debug(f"Request: {request.method}, {request.url}")
    app.logger.debug(f"Request headers: {request.headers}")

  # Home page.
  @app.route("/", methods=['GET'])
  def index():
    return render_template("index.html")

  # Health check.
  @app.route('/status', methods=['POST'])
  def health_check():
    app.logger.debug("health check invoked")
    return jsonify({"status": "OK"}), 200

  @app.route("/admin-screen")
  def admin_screen():
    if not google.authorized:
      app.logger.warning("User is not authorized, redirecting to login")
      return redirect(url_for("google.login"))

    resp = google.get("/oauth2/v2/userinfo")
    user_info = resp.json()
    session["user_email"] = user_info.get("email")

    google_access_token = google.token["access_token"] if google.token else None

    return render_template("admin-screen.html", google_access_token=google_access_token)

  @app.route("/api/folder-selected", methods=["POST"])
  def folder_selected():
    data = request.json
    folder_id = data.get("folder_id")
    folder_name = data.get("folder_name")

    if not folder_id:
      app.logger.error("No folder ID received in selection")
      return jsonify({"error": "No folder selected"}), 400

    session["folder_id"] = folder_id
    session["folder_name"] = folder_name

    app.logger.info(f"User selected folder: {folder_name} (ID: {folder_id})")
    return jsonify({"message": "Folder selected", "folder_id": folder_id})

  # Route for webhook
  @app.route('/webhook', methods=['POST'])
  def webhook():
    app.logger.debug("webhook invoked")
    changed = request.headers.get("X-Goog-Changed")
    channel_id = request.headers.get("X-Goog-Channel-Id")
    resource_id = request.headers.get("X-Goog-Resource-Id")
    resource_uri = request.headers.get("X-Goog-Resource-Uri")
    if not channel_id or not resource_id:
      app.logger.warning("webhook: missing header(s) in request")
      abort(400)
    app.logger.info(f"webhook: channel_id={channel_id}, resource_id={resource_id}")

    installation_id = channel_id.split("-")[1]
    app.logger.info(f"installation_id={installation_id}")

    installation = Installation.query.get(installation_id)
    if not installation:
      logger.error(f"Installation {installation_id} not found.")
      abort(400)
    if installation.status != Installation.Status.IN_SERVICE:
      logger.error(f"Installation {installation_id} not in service ({installation.status}).")
      abort(400)
    # Temporary direct call
    installation = Installation.query.get(installation_id)
    InstallationManager(installation).run_inbox_worker()
    return jsonify({"status": "OK"}), 200

  # Route to add a new Installation
  @app.route('/installation', methods=['POST'])
  @auth_required
  def add_installation():
    data = request.json

    # Validate input fields
    try:
      Installation.validate_installation_values(data)
    except ValueError as ve:
      return ve.args[0], 400

    try:
      # Create a new Installation
      new_installation = Installation.create(
          creator=data['creator'],
          root_folder_id=data['root_folder_id'],
          service_account_info=json.dumps(data['service_account_info']),
      )
      return jsonify(new_installation.to_dict()), 201
    except Exception as e:
      return jsonify({'error': str(e)}), 500

  # Route to mark an Installation for termination
  @app.route('/installation/<int:installation_id>/mark_for_termination', methods=['PATCH'])
  @auth_required
  def mark_for_termination(installation_id):
    try:
      installation = Installation.query.get(installation_id)

      if not installation:
        return jsonify({'error': 'Installation not found'}), 404

      if installation.status == Installation.Status.TERMINATED:
        return jsonify({'error': 'Cannot mark a terminated installation for termination'}), 400

      # Update the status
      installation.update_status(Installation.Status.MARKED_FOR_TERMINATION)

      return jsonify(installation.to_dict()), 200
    except Exception as e:
      return jsonify({'error': str(e)}), 500
