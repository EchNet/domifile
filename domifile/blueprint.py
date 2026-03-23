# domifile/blueprint.py

from flask import Blueprint, jsonify, request, g


def install_blueprint(app):
  #from auth.decorators import require_auth
  from domifile.search.search import answer_question

  bp = Blueprint("domifile", __name__, url_prefix="/api")

  # ------------------------------------------------------------
  # Error Handlers
  # ------------------------------------------------------------

  @bp.errorhandler(KeyError)
  def handle_key_error(e):
    return jsonify(error="not found"), 404

  @bp.errorhandler(PermissionError)
  def handle_permission_error(e):
    return jsonify(error="forbidden"), 403

  @bp.errorhandler(ValueError)
  def handle_value_error(e):
    return jsonify(error=str(e)), 400

  # ------------------------------------------------------------
  # GET /api/ask
  # ------------------------------------------------------------

  @bp.route("/ask", methods=["POST"])
  def ask():
    body = request.get_json(silent=True)
    if not body:
      return jsonify(error="Missing JSON body"), 400

    question = body.question
    if not question:
      return jsonify(error="Missing question"), 400

    answer = answer_question(question)

    return jsonify(answer)

  # --------------------------------------------------------------------

  app.register_blueprint(bp)
