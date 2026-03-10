# domifile/drive/service.py

from google.auth import default
from google.auth.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from .query import _DriveQueryMixin
from .retrieve import _DriveRetrieveMixin

# All Google API authentication flows through Application Default Credentials (ADC).

# Production story:
# Cloud Run / GKE / GCE
# Attach a service account
# Grant IAM roles
# ADC automatically uses the metadata server.

# Development story: Run:
# gcloud auth application-default login

DRIVE_SERVICE_NAME = "drive"
DRIVE_SERVICE_VERSION = "v3"
DRIVE_SERVICE_SCOPE = "https://www.googleapis.com/auth/drive"


class DriveService(_DriveQueryMixin, _DriveRetrieveMixin):
  """
    Google Drive API Connector
  """

  def __init__(self):
    # Initialize credentials:
    self.credentials = self.get_credentials(scopes=[DRIVE_SERVICE_SCOPE])
    # Build service
    self.drive_service = build(DRIVE_SERVICE_NAME,
                               DRIVE_SERVICE_VERSION,
                               credentials=self.credentials,
                               cache_discovery=False)

  @staticmethod
  def get_credentials(*, scopes: list[str] | None = None) -> Credentials:
    creds, _ = default(scopes=scopes)

    if not creds.valid:
      creds.refresh(Request())

    return creds
