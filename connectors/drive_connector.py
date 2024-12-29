# drive_service.py
#
# Wrap the Google Drive services.
#
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from environment import get_service_credentials

# TODO: Add logging and error monitoring.


class DriveService:
  """
    Authenticate using the given parsed service account info structure and build
    a Google Drive service.

    Args:
      credentials    Google Cloud access key structure.
  """
  SCOPES = ["https://www.googleapis.com/auth/drive.file"]

  def __init__(self):
    credentials = get_service_credentials(scopes=self.SCOPES)
    self.drive_service = build("drive", "v3", credentials=credentials)

  def __enter__(self):
    return DriveServiceUtils(self.drive_service)

  # No-op
  def __exit__(self, exc_type, exc_value, traceback):
    pass


class DriveServiceUtils:
  FOLDER_MIME_TYPE = "application/vnd.google-apps.folder"

  # Dictionaries representing files have the following fields.
  FILE_FIELDS = ("id", "name", "mimeType", "parents")

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

  def download_file(self, file_id, output_path):
    """
      Download a file from Google Drive.
      
      Args:
          file_id (str): The ID of the Google Drive file.
          output_path (str): Local path to save the downloaded file.
      
      Returns:
          str: Path to the downloaded file.
    """
    request = self.drive_service.files().get_media(fileId=file_id)
    with io.FileIO(output_path, "wb") as file:
      downloader = MediaIoBaseDownload(file, request)
      done = False
      while not done:
        status, done = downloader.next_chunk()
        print(f"Downloading {file_id} progress: {int(status.progress() * 100)}%")
    return output_path

  def move_file(file_id, new_parent_id):
    """
      Move the file identified by file_id to the folder identified by new_parent_id.
    """
    # Retrieve the file metadata
    file_metadata = self.drive_service.files().get(fileId=file_id, fields="parents").execute()

    # Remove the file from its current parent folder(s), while adding the new parent.
    previous_parents = ",".join(file_metadata.get("parents", []))
    response = self.drive_service.files().update(
        fileId=spreadsheet_id,
        addParents=new_parent_id,
        removeParents=previous_parents,
        fields="id, parents",
    ).execute()
    return response

  def delete_file(file_id):
    """
      Permanently delete a file from Google Drive.

      Args:
          file_id (str): The ID of the file to delete.

      Returns:
          ??
    """
    response = self.drive_service.files().delete(fileId=file_id).execute()
    return response

  def watch_resource(self, resource_id, webhook_url):

    channel_id = f"nestli-{resource_id}"

    watch_request = {
        "id": channel_id,
        "type": "web_hook",
        "address": webhook_url,
    }
    response = self.drive_service.files().watch(fileId=resource_id, body=watch_request).execute()
    return response

  def unwatch_folder(self, resource_id):
    """
      Stop a Google Drive watch channel.
    """
    channel_id = f"nestli-{resource_id}"

    body = {
        "id": channel_id,
        "resourceId": resource_id,
    }
    response = self.drive_service.channels().stop(body=body).execute()
    return response
