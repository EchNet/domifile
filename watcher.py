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

WEBHOOK_URL = "https://hostname/nestli-webhook"


class Watcher:

  def __init__(self, resource_id):
    self.resource_id = resource_id

  def start(self):
    """
      Set up a Google Drive watch on the resource.
    """
    with DriveService() as drive_service:
      response = drive_service.watch_resource(self.resource_id, WEBHOOK_URL)
      # TODO: Log
      return response

  def refresh(self):
    self.cancel()
    self.start()

  def cancel(self):
    with DriveService() as drive_service:
      response = drive_service.unwatch_resource(self.resource_id)
      # TODO: Log
      return response


def scan_inbox():
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
