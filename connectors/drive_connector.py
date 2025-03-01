# drive_service.py
#
# Wrap the Google Drive services.
#
import io
from environment import ServiceAccountInfo
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from .file import File, FOLDER_MIME_TYPE

# Dictionaries representing files have the following fields.
FILE_FIELDS = ("id", "name", "mimeType", "parents", "properties", "owners")
FILE_FIELDS_SPEC = ", ".join(FILE_FIELDS)


class DriveFileNotFoundError(Exception):
  pass


class DriveAccessDeniedError(Exception):
  pass


def raise_error_from_http_error(http_error, message):
  error_code = http_error.resp.status
  if error_code == 404:
    raise DriveFileNotFoundError(f"{message} - file not found") from http_error
  elif error_code == 403:
    raise DriveAccessDeniedError(f"{message} - access denied") from http_error
  else:
    raise http_error


class DriveConnector:
  """ Google Drive API Connector """

  SCOPES = ["https://www.googleapis.com/auth/drive"]

  def __init__(self, service_account_info=None):
    """
      Authenticate using the given parsed service account info structure and build
      a Google Drive service.

      Args:
        service_account_info    Google Cloud service account credenials.
    """
    if isinstance(service_account_info, str):
      service_account_info = ServiceAccountInfo.from_json_string(service_account_info)
    if not service_account_info:
      service_account_info = ServiceAccountInfo.from_env("GOOGLE_SERVICE_ACCT_CREDENTIALS")
    credentials = service_account_info.get_scoped_credentials(scopes=self.SCOPES)
    self.drive_service = build("drive", "v3", credentials=credentials)

  def __enter__(self):
    return self

  # No-op
  def __exit__(self, exc_type, exc_value, traceback):
    # If there were cleanup to be done, it would be done here.
    pass

  def get(self, file_id):
    """ Fetch a file by its ID. """
    try:
      f = self.drive_service.files().get(fileId=file_id, fields=FILE_FIELDS_SPEC).execute()
      return File(f)
    except HttpError as error:
      raise_error_from_http_error(error, f"Cannot get file {file_id}")

  def query(self):
    """
      List Google Drive files that match query filters.

      Returns:
        A builder of a Google Drive query.

        The bulder supports the following filters:
          .named("name")
          .children_of(folder_id)
          .only_folders()
          .excluding_folders()

        To execute the completed query:
          .list()

          Returns:
            list: A list of file metadata

        Or, in case one or zero matches are expected:
          .get()

          Returns:
            a File or null.

        Example:
          files = drive_service.query().named("INBOX").children_of(folder_id).get()
    """

    class QueryBuilder:

      def __init__(self, drive_service):
        self.query_parts = ["trashed=false"]
        self.drive_service = drive_service

      def named(self, name):
        self.query_parts.append(f"name='{name}'")
        return self

      def children_of(self, parent_id):
        self.query_parts.append(f"'{parent_id}' in parents")
        return self

      def only_folders(self):
        self.query_parts.append(f"mimeType='{FOLDER_MIME_TYPE}'")
        return self

      def excluding_folders(self):
        self.query_parts.append(f"mimeType != '{FOLDER_MIME_TYPE}'")
        return self

      def list(self):
        query = " and ".join(self.query_parts)
        # TODO: allow pagination
        results = self.drive_service.files().list(
            q=query,
            fields=f"files({FILE_FIELDS_SPEC})",
        ).execute()
        files = results.get("files", [])
        return [File(f) for f in files]

      def get(self):
        all = self.list()
        return all[0] if all else None

    return QueryBuilder(self.drive_service)

  def create_folder(self, name, parent, owner=None):
    """
      Create a folder in Google Drive.

      Args:
          name (str): Name of the new folder.
          parent (str): ID of the parent folder.
          owners (str, optional): Email address of the desired owner

      Returns:
          str: The ID of the created folder.
    """
    print(f"Drive: Creating new folder {name}")

    # Create the folder
    folder = self.drive_service.files().create(
        body={
            "name": name,
            "mimeType": FOLDER_MIME_TYPE,
            "parents": [parent]
        },
        fields=FILE_FIELDS_SPEC,
    ).execute()
    folder = File(folder)

    print(f"Drive: Created new folder {name}")

    # Change ownership.
    if owner and owner != folder.owner:
      try:
        self.drive_service.permissions().create(
            fileId=folder.id,
            body={
                'type': 'user',
                'role': 'owner',
                'emailAddress': owner,
            },
            transferOwnership=True,
        ).execute()

        print(f"Drive: ownership of {name} transferred to {owner}")
        folder.owner = owner

      except Exception as e:
        print(f"Drive: WARNING: ownership of {name} not transferred to {owner} - {e}")

    return folder

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
    print(response)

  def delete_file(file_id):
    """
      Permanently delete a file from Google Drive.

      Args:
          file_id (str): The ID of the file to delete.

      Returns:
          ??
    """
    response = self.drive_service.files().delete(fileId=file_id).execute()
    print(response)

  def create_watch_channel(self, *, channel_id, file_id, webhook_url):
    """
      Create a watch channel via which notifications of modifications to a given file 
      or folder are sent to the given webhook URL.

      Parameters
        channel_id   (str) A unique string to identify the channel.
        file_id      (str) The drive ID of the source folder
        webhook_url  (str) The URL of the webhook

      Returns
        (str) The resource ID of the watch channel, needed for closing the channel.
    """
    print(f"Watcher: CREATING watch channel channel_id={channel_id}")

    response = self.drive_service.files().watch(fileId=file_id,
                                                body={
                                                    "id": channel_id,
                                                    "type": "web_hook",
                                                    "address": webhook_url,
                                                }).execute()
    resource_id = response["resourceId"]
    print(f"Watcher: CREATED watch channel channel_id={channel_id}, resource_id={resource_id}")
    return resource_id

  def close_watch_channel(self, *, channel_id, resource_id):
    """
      Close a Google Drive watch channel.

      Parameters
        channel_id   (str) A unique string to identify the channel.
        resource_id  (str) The resource ID of watch channel, as returned by create_watch_channel.

      Returns
        None
    """
    print(f"Watcher: CLOSING watch channel resource_id={resource_id}, channel_id={channel_id}")

    try:
      self.drive_service.channels().stop(body={
          "id": channel_id,
          "resourceId": resource_id,
      }).execute()
    except HttpError as error:
      raise_error_from_http_error(error, "Cannot close watch channel {channel_id}")

    print(f"Watcher: CLOSED watch channel")

  def set_file_metadata(self, file_id, metadata):
    print(f"Drive Connector: set metadata={metadata} on file={file_id}")
    assert isinstance(metadata, dict), "metadata must be a dict"
    result = self.drive_service.files().update(
        fileId=file_id,
        body={
            "properties": metadata
        },
        fields="id, properties",
    ).execute()
    print(f"Drive Connector: {result}")
