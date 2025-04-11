# DriveQueryMixin.py

from connectors.drive.DriveFile import DriveFile
from connectors.drive.decorators import drive_file_id_operation
from connectors.drive.errors import DriveFileNotFoundError, http_error_handling


class DriveQueryMixin:
  """
    Wrapper for Google Drive services related to file search.
  """

  def __init__(self, drive_service):
    self.drive_service = drive_service

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
            list: A list of DriveFiles

        Or, in case one or zero matches are expected:
          .first()

          Returns:
            a DriveFile or null.

        Or, in case exactly one match is expected:
          .get()
        Returns:
          a DriveFile (otherwise, raises DriveFileNotFoundError)

        Example:
          files = dq.query().named("INBOX").children_of(folder_id).get()
    """

    class QueryBuilder:

      def __init__(self, drive_service):
        self.drive_service = drive_service
        self.query_parts = []
        self.post_filters = []
        self.include_trashed = False

      def named(self, name):
        self.query_parts.append(f"name='{name}'")
        return self

      @drive_file_id_operation()
      def children_of(self, parent_id):
        self.query_parts.append(f"'{parent_id}' in parents")
        return self

      def only_folders(self):
        self.query_parts.append(f"mimeType='{DriveFile.FOLDER_MIME_TYPE}'")
        return self

      def excluding_folders(self):
        self.query_parts.append(f"mimeType != '{DriveFile.FOLDER_MIME_TYPE}'")
        return self

      def including_trashed(self):
        self.include_trashed = True
        return self

      def having_property(self, prop_name):
        self.post_filters.append(lambda f: bool(f.get("properties", {}).get(prop_name)))
        return self

      def _list(self):
        query_parts = self.query_parts
        if not self.include_trashed:
          query_parts.append("trashed=false")
        query = " and ".join(query_parts)
        # TODO: allow pagination
        with http_error_handling("Listing files that match filters"):
          results = self.drive_service.files().list(
              q=query,
              fields=f"files({DriveFile.FIELDS_SPEC})",
          ).execute()
        files = results.get("files", [])
        for filt in self.post_filters:
          files = filter(filt, files)
        return files

      def list(self):
        files = self._list()
        return [DriveFile(f) for f in files]

      def first(self):
        all = self._list()
        return DriveFile(all[0]) if all else None

      def get(self):
        all = self._list()
        if not all:
          raise DriveFileNotFound("No file found matching the filter criteria.")
        if len(all) > 1:
          raise ValueError(f"More than one file ({len(all)}) found matching the filter criteria.")
        return DriveFile(all[0])

    return QueryBuilder(self.drive_service)
