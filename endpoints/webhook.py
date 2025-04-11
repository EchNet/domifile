# endpoints/webhook.py

import logging

logger = logging.getLogger(__name__)


def define_webhook_endpoints(app):

  from flask import abort, request, jsonify
  from models.Installation import Installation
  from tasks.bucket_tasks import run_bucket_action

  # Route for webhook
  @app.route('/webhook', methods=['POST'])
  def webhook():
    logger.debug("webhook invoked")

    channel_id = request.headers.get("X-Goog-Channel-ID")
    channel_token = request.headers.get("X-Goog-Channel-Token")
    resource_id = request.headers.get("X-Goog-Resource-ID")
    resource_uri = request.headers.get("X-Goog-Resource-URI")
    resource_state = request.headers.get("X-Goog-Resource-State")
    message_number = request.headers.get("X-Goog-Message-Number")
    logger.info(f"webhook: channel_id={channel_id} "
                f"channel_token={channel_token} "
                f"resource_id={resource_id} "
                f"resource_uri={resource_uri} "
                f"resource_state={resource_state} "
                f"message_number={message_number}")

    if not channel_id or not resource_id:
      logger.error("webhook: missing header(s) in request")
      abort(400)

    try:
      installation_id = channel_id.split("-")[1]
      folder_id = channel_id.split("-")[2]
    except:
      logger.error(f"webhook: bad channel id {channel_id}")
      abort(400)

    app.invoke_shared_task(run_bucket_action, [installation_id, folder_id])
    return jsonify({"status": "OK"}), 200
