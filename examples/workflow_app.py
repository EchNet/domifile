from flask import Flask, request, jsonify
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.cloud import secretmanager
import json
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)

# GCP Config
PROJECT_ID = "your_project_id"
SECRET_NAME = "domifile-oauth-tokens"
SCOPES = [
    "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/calendar", "https://www.googleapis.com/auth/gmail.send"
]


def get_stored_credentials():
  """Retrieve refresh token from Secret Manager and use it to get credentials."""
  client = secretmanager.SecretManagerServiceClient()
  name = f"projects/{PROJECT_ID}/secrets/{SECRET_NAME}/versions/latest"
  response = client.access_secret_version(request={"name": name})
  secret_data = json.loads(response.payload.data.decode("UTF-8"))

  credentials = Credentials.from_authorized_user_info(secret_data, SCOPES)
  return credentials


def send_email(recipient, subject, message_body):
  """Send email using Gmail API."""
  credentials = get_stored_credentials()
  gmail_service = build("gmail", "v1", credentials=credentials)

  # Create Email Message
  message = MIMEMultipart()
  message["to"] = recipient
  message["subject"] = subject
  message.attach(MIMEText(message_body, "html"))
  raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

  # Send Email
  gmail_service.users().messages().send(userId="me", body={"raw": raw_message}).execute()


def workflow_notification(file_id, metadata):
  """Send email notification for workflow events."""
  subject = f"New Invoice Received: {metadata['vendor']}"
  message_body = f"""
    <h3>New Invoice Received</h3>
    <p><strong>Date:</strong> {metadata['date']}</p>
    <p><strong>Amount:</strong> {metadata['amount']}</p>
    <p><strong>Vendor:</strong> {metadata['vendor']}</p>
    <p><a href="https://drive.google.com/open?id={file_id}">View Document</a></p>
    """
  treasurer_email = "treasurer@example.com"
  send_email(treasurer_email, subject, message_body)


@app.route("/start_workflow", methods=["POST"])
def start_workflow():
  """Start Workflow when new file is detected."""
  data = request.get_json()
  file_id = data["file_id"]
  workflow_type = data["workflow_type"]

  # Example Metadata (In reality, extract this from the document)
  metadata = {
      "date": "2025-03-01",
      "amount": "500.00",
      "vendor": "ABC Supplies",
      "due_date": "2025-03-15T09:00:00-05:00"
  }

  workflow_notification(file_id, metadata)
  return jsonify({"message": "Workflow initiated and notification sent."})


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=8080)
