# environment.py
#
# Extract configuration values from environment variables.
#
import json
import os
from google.oauth2.service_account import Credentials


def get_service_account_info():
  SERVICE_ACCOUNT_CREDENTIALS_ENV_NAME = "GOOGLE_SERVICE_ACCT_CREDENTIALS"

  if SERVICE_ACCOUNT_CREDENTIALS_ENV_NAME not in os.environ:
    raise EnvironmentError(
        f"The {SERVICE_ACCOUNT_CREDENTIALS_ENV_NAME} environment variable is not set.")

  credentials_json = os.environ[SERVICE_ACCOUNT_CREDENTIALS_ENV_NAME]
  return json.loads(credentials_json)


def get_service_credentials(scopes):
  service_account_info = get_service_account_info()
  credentials = Credentials.from_service_account_info(service_account_info, scopes=scopes)
  return credentials
