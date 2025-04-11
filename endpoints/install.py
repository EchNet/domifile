# endpoints/install.py


def define_install_endpoints(app):
  """
   Define API methods for creating, retrieving and terminating installations.
  """
  from auth import auth_required
  from flask import jsonify
  from models.Installation import Installation

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
