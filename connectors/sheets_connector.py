# sheets_service.py
#
# Wrap the Google Sheets services.
#

from googleapiclient.discovery import build
from environment import get_service_credentials


class SheetsService:
  """
    Build a Google Sheets service.
  """
  SERVICE_NAME = "sheets"
  VERSION = "v4"
  SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

  def __init__(self, service_account_info=None):
    if not service_account_info:
      service_account_info = ServiceAccountInfo.from_env("GOOGLE_SERVICE_ACCT_CREDENTIALS")
    credentials = service_account_info.get_scoped_credentials(scopes=self.SCOPES)
    self.sheets_service = build(self.SERVICE_NAME, self.VERSION, credentials=credentials)

  def __enter__(self):
    return self

  # No-op
  def __exit__(self, exc_type, exc_value, traceback):
    pass

  def open_document(self, sheet_document_id):
    # TODO: validate document ID before continuing
    return SheetsDocumentWrapper(self.sheets_service, sheet_document_id)

  def create_document(self, name, parent_id=None):
    """
      Create a new Google Sheets document and write a value into the specified cell.

      Args:
          name (str): The title of the new Google Sheets document.
          parent_id (str): The ID of the parent folder (or None for the default)

      Returns:
          str: The ID of the newly created Google Sheets document.
    """
    body = {"properties": {"title": name}}
    document = sheets_service.spreadsheets().create(body).execute()
    spreadsheet_id = document["spreadsheetId"]
    return spreadsheet_id


class SheetsDocumentWrapper:
  """
  """

  def __init__(self, sheets_service, sheet_document_id):
    self.sheets_service = sheets_service
    self.sheet_document_id = sheet_document_id

  def list_sheet_titles(self):
    sheets_metadata = self.sheets_service.spreadsheets().get(
        spreadsheetId=self.sheet_document_id).execute()
    tabs = sheets_metadata.get("sheets", [])
    return [s.get("properties", {}).get("title") for s in sheets]

  def open_sheet_by_title(self, sheet_title):
    # TODO: Validate sheet title first.
    return SheetWrapper(self.sheets_service, self.sheet_document_id, sheet_title)


class SheetWrapper:
  """
  """

  def __init__(self, sheets_service, sheet_document_id, sheet_title):
    self.sheets_service = sheets_service
    self.sheet_document_id = sheet_document_id
    self.sheet_title = sheet_title

  def get_values(self):
    """
    """
    values = self.sheets_service.spreadsheets().values()
    data = values.get(spreadsheetId=self.sheet_document_id, range=self.sheet_title).execute()
    return data.get("values", [])

  def append_row(self, row_data):
    """
    """
    self.sheets_service.spreadsheets().values().append(spreadsheetId=self.sheet_document_id,
                                                       range=f"{self.tab_title}!A1",
                                                       body={
                                                           "majorDimension": "ROWS",
                                                           "values": [row_data],
                                                       },
                                                       valueInputOption="RAW").execute()

  def write_to_cell(self, cell_address, cell_value):
    """
    """
    update_body = {"range": cell_address, "values": [[cell_value]]}
    response = self.sheets_service.spreadsheets().values().update(spreadsheetId=spreadsheet_id,
                                                                  range=cell,
                                                                  valueInputOption="RAW",
                                                                  body={
                                                                      "values": [[cell_value]]
                                                                  }).execute()
    return response
