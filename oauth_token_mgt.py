from flask import Flask, redirect, url_for, session, request, jsonify
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.cloud import secretmanager
import json
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Google OAuth Settings
CLIENT_SECRETS_FILE = "client_secrets.json"
SCOPES = ["https://www.googleapis.com/auth/drive.file"]
REDIRECT_URI = "http://localhost:5000/oauth2callback"
SECRET_NAME = "domofile-oauth-tokens"
PROJECT_ID = "your_gcp_project_id"


def get_secret_manager_client():
  return secretmanager.SecretManagerServiceClient()


@app.route("/")
def index():
  return "Welcome to Domofile OAuth Management"


@app.route("/login")
def login():
  flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE,
                                       scopes=SCOPES,
                                       redirect_uri=REDIRECT_URI)
  auth_url, state = flow.authorization_url(access_type="offline", include_granted_scopes="true")
  session["state"] = state
  return redirect(auth_url)


@app.route("/oauth2callback")
def oauth2callback():
  state = session["state"]
  flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE,
                                       scopes=SCOPES,
                                       state=state,
                                       redirect_uri=REDIRECT_URI)
  flow.fetch_token(authorization_response=request.url)

  credentials = flow.credentials
  store_credentials(credentials)

  return jsonify({"message": "Login successful", "tokens": credentials_to_dict(credentials)})


def store_credentials(credentials):
  """Store refresh token securely in Secret Manager."""
  client = get_secret_manager_client()
  secret_data = json.dumps({
      "refresh_token": credentials.refresh_token,
      "client_id": credentials.client_id,
      "client_secret": credentials.client_secret,
      "token_uri": credentials.token_uri
  })

  parent = f"projects/{PROJECT_ID}"
  try:
    # Check if secret version exists, if not, create a new one
    response = client.access_secret_version(
        request={"name": f"{parent}/secrets/{SECRET_NAME}/versions/latest"})
    # Add a new version with updated token
    client.add_secret_version(request={
        "parent": f"{parent}/secrets/{SECRET_NAME}",
        "payload": {
            "data": secret_data.encode("UTF-8")
        }
    })
  except Exception:
    # If secret doesn't exist, create it
    client.create_secret(request={
        "parent": parent,
        "secret_id": SECRET_NAME,
        "secret": {
            "replication": {
                "automatic": {}
            }
        }
    })
    client.add_secret_version(request={
        "parent": f"{parent}/secrets/{SECRET_NAME}",
        "payload": {
            "data": secret_data.encode("UTF-8")
        }
    })


def get_stored_credentials():
  """Retrieve refresh token from Secret Manager and use it to get credentials."""
  client = get_secret_manager_client()
  name = f"projects/{PROJECT_ID}/secrets/{SECRET_NAME}/versions/latest"
  response = client.access_secret_version(request={"name": name})
  secret_data = json.loads(response.payload.data.decode("UTF-8"))

  credentials = Credentials.from_authorized_user_info(secret_data, SCOPES)
  if credentials and credentials.expired and credentials.refresh_token:
    credentials.refresh(Request())

  return credentials


@app.route("/list_files")
def list_files():
  """Example API to list files in Drive using stored credentials."""
  credentials = get_stored_credentials()
  if not credentials:
    return redirect(url_for("login"))

  drive_service = build("drive", "v3", credentials=credentials)
  results = drive_service.files().list(pageSize=10,
                                       fields="nextPageToken, files(id, name)").execute()

  return jsonify({"files": results.get("files", [])})


def credentials_to_dict(credentials):
  return {
      "token": credentials.token,
      "refresh_token": credentials.refresh_token,
      "token_uri": credentials.token_uri,
      "client_id": credentials.client_id,
      "client_secret": credentials.client_secret,
      "scopes": credentials.scopes
  }


if __name__ == "__main__":
  app.run(debug=True)
