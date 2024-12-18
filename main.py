import argparse
import os
import json
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

CREDENTIALS_ENV_NAME = "GOOGLE_SERVICE_ACCT_CREDENTIALS"
SCOPES = ["https://www.googleapis.com/auth/drive"]

# Get credentials from the environment
if CREDENTIALS_ENV_NAME not in os.environ:
  raise EnvironmentError("The GOOGLE_APPLICATION_CREDENTIALS environment variable is not set.")
credentials_json = os.environ[CREDENTIALS_ENV_NAME]
credentials_obj = json.loads(credentials_json)

# Parse credentials
credentials = Credentials.from_service_account_info(credentials_obj, scopes=SCOPES)

# Initialize the Google Drive API client
drive_service = build("drive", "v3", credentials=credentials)


# Function to list files in a folder
def list_files_in_folder(folder_id):
  """List files in the specified folder."""
  query = f"'{folder_id}' in parents and trashed = false"
  results = drive_service.files().list(q=query, fields="files(id, name, createdTime)").execute()

  files = results.get("files", [])
  return files
  print(f"Found file: {file['name']} (ID: {file['id']})")


# Command-line argument parsing
arg_parser = argparse.ArgumentParser(description="Process a Google Drive folder.")
arg_parser.add_argument("folder_id", help="The ID of the folder to process.")
args = arg_parser.parse_args()

# Use the folder ID from the command line
inbox_folder_id = args.folder_id

# Example usage
files = list_files_in_folder(inbox_folder_id)

print(f"Files in folder {inbox_folder_id}:")
for file in files:
  print(f" - \"{file['name']}\" (ID: {file['id']})")
