import json
import os


def get_service_account_info_from_environment():
  SERVICE_ACCOUNT_CREDENTIALS_ENV_NAME = "GOOGLE_SERVICE_ACCT_CREDENTIALS"

  if SERVICE_ACCOUNT_CREDENTIALS_ENV_NAME not in os.environ:
    raise EnvironmentError(
        f"The {SERVICE_ACCOUNT_CREDENTIALS_ENV_NAME} environment variable is not set.")

  credentials_json = os.environ[SERVICE_ACCOUNT_CREDENTIALS_ENV_NAME]
  return json.loads(credentials_json)
