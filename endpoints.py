# endpoints.py
#
# API methods for creating, retrieving and terminating installations.
#

from flaskapp import flaskapp as app


# Route to add a new Installation
@app.route('/installations', methods=['POST'])
def add_installation():
  data = request.json

  # Validate required fields
  if not all(key in data for key in ['creator', 'inbox_id', 'service_account_info']):
    return jsonify({'error':
                    'Missing required fields: creator, inbox_id, service_account_info'}), 400

  try:
    # Validate status
    status = data.get('status', 'READY')
    if status not in STATUS_OPTIONS:
      return jsonify({'error':
                      f"Invalid status. Allowed statuses: {', '.join(STATUS_OPTIONS)}"}), 400

    # Create a new Installation
    new_installation = Installation(creator=data['creator'],
                                    inbox_id=data['inbox_id'],
                                    service_account_info=json.dumps(data['service_account_info']),
                                    status=status)
    db.session.add(new_installation)
    db.session.commit()

    return jsonify(new_installation.to_dict()), 201
  except Exception as e:
    return jsonify({'error': str(e)}), 500


# Route to mark an Installation for termination
@app.route('/installations/<int:installation_id>/mark_for_termination', methods=['PATCH'])
def mark_for_termination(installation_id):
  try:
    installation = Installation.query.get(installation_id)

    if not installation:
      return jsonify({'error': 'Installation not found'}), 404

    if installation.status in {'TERMINATED'}:
      return jsonify({'error': 'Cannot mark a terminated installation for termination'}), 400

    # Update the status
    installation.status = 'MARKED_FOR_TERMINATION'
    db.session.commit()

    return jsonify(installation.to_dict()), 200
  except Exception as e:
    return jsonify({'error': str(e)}), 500


# Route to list all Installations
@app.route('/installations', methods=['GET'])
def list_installations():
  try:
    installations = Installation.query.all()
    return jsonify([installation.to_dict() for installation in installations]), 200
  except Exception as e:
    return jsonify({'error': str(e)}), 500


# Run server
def run_flask_app():
  PORT = 8080
  app.run(host='0.0.0.0', port=PORT)
