from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build


class DriveService:
  """
    Authenticate using the given parsed service account info structure and build
    a Google Drive service.

    Args:
      credentials    Google Cloud access key structure.
  """
  SCOPES = ["https://www.googleapis.com/auth/drive"]

  def __init__(self, service_account_info):
    self.service_account_info = service_account_info

  def __enter__(self):
    credentials = Credentials.from_service_account_info(self.service_account_info,
                                                        scopes=self.SCOPES)
    drive_service = build("drive", "v3", credentials=credentials)
    return DriveServiceUtils(drive_service)

  # No-op
  def __exit__(self, exc_type, exc_value, traceback):
    pass


class DriveServiceUtils:

  def __init__(self, drive_service):
    self.drive_service = drive_service

  def find_folders_by_name(self, folder_name):
    """
      List all accessible folders of a certain name.

      Args:
          folder_name (str): The name of the folders.

      Returns:
        list: A list of dictionaries representing files and having the following fields: id, name
    """
    query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and trashed=false"
    return self.query_for_files(query)

  def list_files_in_folder(self, folder_id):
    """
      List all files in a specified folder.

      Args:
          folder_id (str): The ID of the folder.

      Returns:
        list: A list of dictionaries representing files and having the following fields: id, name
    """
    query = f"'{folder_id}' in parents and trashed = false"
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
        list: A list of dictionaries representing files and having the following fields: id, name
    """
    results = self.drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])
    return files
