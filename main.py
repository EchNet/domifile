import os
import json
from drive_service import DriveService

#
# This is the program that runs every few seconds to discover new files in the inbox.
#
# It is bound to a specific service account via a set of credentials, which is specified via
# the environment variable GOOGLE_SERVICE_ACCT_CREDENTIALS, the value of which is a JSON
# string.
#
# Find all of the Nestli folders accessible by the service account.  For each, list the contents
# of the INBOX subfolder.  Fire up a worker process to handle each new file.
#

SERVICE_ACCOUNT_CREDENTIALS_ENV_NAME = "GOOGLE_SERVICE_ACCT_CREDENTIALS"

# TODO: Add logging and error monitoring.


def get_credentials_from_environment():
  if SERVICE_ACCOUNT_CREDENTIALS_ENV_NAME not in os.environ:
    raise EnvironmentError(
        f"The {SERVICE_ACCOUNT_CREDENTIALS_ENV_NAME} environment variable is not set.")
  credentials_json = os.environ[SERVICE_ACCOUNT_CREDENTIALS_ENV_NAME]
  return json.loads(credentials_json)


credentials = get_credentials_from_environment()
with DriveService(credentials) as drive_utils:

  # Find all folders named INBOX accessible to this service account.
  for inbox in drive_utils.find_folders_by_name("INBOX"):

    inbox_id = inbox["id"]

    parent_folder_ids = drive_utils.get_parent_folder_ids(inbox_id)
    if parent_folder_ids:
      parent_id = parent_folder_ids.pop(0)
      if parent_folder_ids:
        print(f"{inbox_id}: More than one parent is not allowed!")  # FIXME
        continue

    files = drive_utils.list_files_in_folder(inbox_id)
    for file in files:
      file_id = file["id"]
      file_name = file["name"]
      print(f"{file_id} {file_name}")
