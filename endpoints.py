# endpoints.py
#
# API methods for creating, retrieving and terminating installations.
#
import logging

logger = logging.getLogger(__name__)


def define_endpoints(app):

  from auth import auth_required
  from flask import abort, request, jsonify
  from managers.installation_manager import InstallationManager
  from models.installation import Installation

  @app.before_request
  def log_request():
    print(request.method, request.url)
    print(request.headers)

  # Route for webhook
  @app.route('/webhook', methods=['POST'])
  def webhook():
    print("webhook invoked")
    changed = request.headers.get("X-Goog-Changed")
    channel_id = request.headers.get("X-Goog-Channel-Id")
    resource_id = request.headers.get("X-Goog-Resource-Id")
    resource_uri = request.headers.get("X-Goog-Resource-Uri")
    if not channel_id or not resource_id:
      print("webhook: missing header(s) in request")
      abort(400)
    print(f"webhook: channel_id={channel_id}, resource_id={resource_id}")

    installation_id = channel_id.split("-")[1]
    print(f"installation_id={installation_id}")

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
