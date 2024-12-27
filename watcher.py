# watcher.py
#
# Responsibilies: for notifications from Drive that the contents of a folder have changed,
#
# It is bound to a specific service account via a set of credentials, which is specified via
# the environment variable GOOGLE_SERVICE_ACCT_CREDENTIALS, the value of which is a JSON
# string.
#
# Find all of the Nestli folders accessible by the service account.  For each, list the contents
# of the INBOX subfolder.  Fire up a worker process to handle each new file.
#

from multiprocessing import Pool
from drive_service import DriveService
from worker import run_file_worker


def setup_inbox_watcher(inbox_folder_id, webhook_url):
  """
    Set up a Google Drive watch on a folder.  May be called multiple times without
    creating redundancy.  Should be called once daily to refresh the channel.
    
    Args:
        folder_id (str): The ID of the folder to watch.
        webhook_url (str): The URL of the webhook endpoint.
    
    Returns:
        dict: The watch response from the Google Drive API.
  """
  with DriveService() as drive_service:
    channel_info = drive_service.get_watch_channel()

    WEBHOOK_URL = "https://hostname/nestli-webhook"


    response = drive_service.files().watch(fileId=folder_id, body=watch_request).execute()
    return response


def scan_inbox_
      # Find all files (not folders) in this inbox.
      files = drive_service.list_files_in_folder(inbox["id"])

      job_params.extend([(file["id"], file["name"], file["mimeType"]) for file in files])

    def run_job(args):
      file_id, file_name, mime_type = args
      run_file_worker(file_id, file_name, mime_type)

    # Run all jobs.
    with Pool(processes=4) as pool:
      pool.map(run_job, job_params)

    print("All jobs have finished. Cleaning up...")


# Replace with your folder ID and webhook URL
folder_id = "your-folder-id"
webhook_url = "https://your-webhook-url.com/handle-drive-event"
response = setup_watch(folder_id, webhook_url)
print("Watch response:", response)

if __name__ == "__main__":

  with DriveService() as drive_service:

    job_params = []

    # Find all folders named INBOX accessible to this service account.
    for inbox in drive_service.find_folders_by_name("INBOX"):

