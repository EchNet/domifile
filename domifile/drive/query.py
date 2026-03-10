# domifile/drive/query.py

from .types import DriveFile
from .errors import DriveFileNotFoundError, http_error_handling


class _DriveQueryMixin:
  """
    Wrapper for Google Drive services related to file search.
  """

  def query(self):
    """
      List Google Drive files that match query filters.

      Returns:
        A builder of a Google Drive query.

        The builder supports the following filters:
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
        query_parts = list(self.query_parts)
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
        files = self._list()
        return DriveFile(files[0]) if files else None

      def get(self):
        files = self._list()
        if not files:
          raise DriveFileNotFoundError("No file found matching the filter criteria.")
        if len(files) > 1:
          raise ValueError(
              f"More than one file ({len(files)}) found matching the filter criteria.")
        return DriveFile(files[0])

    return QueryBuilder(self.drive_service)
