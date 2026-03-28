# domifile/drive/retrieve.py

import io
import logging
from googleapiclient.http import MediaIoBaseDownload
from pathlib import Path

from .types import DriveFile
from .errors import http_error_handling

logger = logging.getLogger(__name__)


class _DriveRetrieveMixin:
  """
    Wrapper for Google Drive services related to file data and metadata retrieval.
  """

  def get(self, file_id):
    """ Fetch file metadata by file ID. """
    with http_error_handling(f"Retrieve file metadata {file_id}"):
      f = self.drive_service.files().get(fileId=file_id, fields=DriveFile.FIELDS_SPEC).execute()
      return DriveFile(f)

  def download_file(self, file, *, tmpdir, export_mime_type=None):
    """
      Download a file from Google Drive.
      
      Args:
          file (DriveFile): The Google Drive file.
          tmpdir (str): Path name of local temp directory.
          export_mime_type (str): Target mime type, if exporting
      
      Returns:
          str: Path to the downloaded file.
    """
    logger.debug(f"download_file {file.id} {file.name} {tmpdir}")
    with http_error_handling(f"Download file {file.id}"):
      if export_mime_type:
        request = self.drive_service.files().export_media(fileId=file.id,
                                                          mimeType=export_mime_type)
        ext = file.name.rsplit('.', 1)[-1] if '.' in file.name else ''
      else:
        request = self.drive_service.files().get_media(fileId=file.id)
        ext = ""

      output_path = Path(tmpdir) / f"{file.id}{'.' if ext else ''}{ext}"

      with io.FileIO(output_path, "wb") as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
          status, done = downloader.next_chunk()
          if status:
            logger.debug(f"Downloading {file.id} progress: {int(status.progress() * 100)}%")

    return str(output_path)

    # TODO: balk at files that are beyond a certain size
