import json
import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# TODO: Add logging and error monitoring.


def get_service_account_info_from_environment():
  SERVICE_ACCOUNT_CREDENTIALS_ENV_NAME = "GOOGLE_SERVICE_ACCT_CREDENTIALS"

  if SERVICE_ACCOUNT_CREDENTIALS_ENV_NAME not in os.environ:
    raise EnvironmentError(
        f"The {SERVICE_ACCOUNT_CREDENTIALS_ENV_NAME} environment variable is not set.")

  credentials_json = os.environ[SERVICE_ACCOUNT_CREDENTIALS_ENV_NAME]
  return json.loads(credentials_json)


class DriveService:
  """
    Authenticate using the given parsed service account info structure and build
    a Google Drive service.

    Args:
      credentials    Google Cloud access key structure.
  """
  SCOPES = ["https://www.googleapis.com/auth/drive"]

  def __init__(self):
    self.service_account_info = get_service_account_info_from_environment()

  def __enter__(self):
    credentials = Credentials.from_service_account_info(self.service_account_info,
                                                        scopes=self.SCOPES)
    drive_service = build("drive", "v3", credentials=credentials)
    return DriveServiceUtils(drive_service)

  # No-op
  def __exit__(self, exc_type, exc_value, traceback):
    pass


class DriveServiceUtils:
  FOLDER_MIME_TYPE = "application/vnd.google-apps.folder"

  # Dictionaries representing files have the following fields.
  FILE_FIELDS = ("id", "name", "parents")

  def __init__(self, drive_service):
    self.drive_service = drive_service

  def find_folders_by_name(self, folder_name):
    """
      List all folders of a certain name that are accessible by the service account bound to 
      this Drive service.

      Args:
          folder_name (str): The name of the folders.

      Returns:
        list: A list of dictionaries representing files
    """
    query = f"mimeType='{self.FOLDER_MIME_TYPE}' and name='{folder_name}' and trashed=false"
    return self.query_for_files(query)

  def list_files_in_folder(self, folder_id):
    """
      List all files, excluding folders, in a specified folder.

      Args:
          folder_id (str): The ID of the folder.

      Returns:
        list: A list of dictionaries representing files and having the following fields: id, name
    """
    query = f"'{folder_id}' in parents and mimeType != '{self.FOLDER_MIME_TYPE}' and trashed = false"
    return self.query_for_files(query)

  def get_parent_folder_ids(self, file_id):
    """
      Retrieve the parent folder ID of a file given its ID.

      Args:
          file_id (str): The ID of the file.

      Returns:
          list: A list of parent folder IDs (can be multiple if the file is in shared drives or multiple folders).
      """
    # Retrieve the file metadata including parent folder(s)
    file_metadata = self.drive_service.files().get(fileId=file_id, fields="parents").execute()

    # Get the parent folder IDs
    parent_ids = file_metadata.get("parents", [])
    return parent_ids

  def query_for_files(self, query):
    """
      List files that match the given query.

      Args:
          query (str): A Google Drive query.

      Returns:
        list: A list of dictionaries representing files
    """
    # TODO: allow pagination
    results = self.drive_service.files().list(
        q=query, fields=f"files({', '.join(self.FILE_FIELDS)})").execute()
    files = results.get("files", [])
    return files

  def create_folder(folder_name, parent_folder_id=None):
    """
      Create a folder in Google Drive.

      Args:
          folder_name (str): Name of the new folder.
          parent_folder_id (str, optional): ID of the parent folder. If None, the folder is created at the root level.

      Returns:
          str: The ID of the newly created folder.
    """
    # Folder metadata
    folder_metadata = {
        "name": folder_name,
        "mimeType": self.FOLDER_MIME_TYPE,
    }

    # If a parent folder is specified, set it
    if parent_folder_id:
      folder_metadata["parents"] = [parent_folder_id]

    # Create the folder
    folder = self.drive_service.files().create(body=folder_metadata, fields="id").execute()

    print(f"Folder '{folder_name}' created with ID: {folder['id']}")
    return folder["id"]
