# watcher.py
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

from multiprocessing import Pool
from drive_service import DriveService
from worker import run_file_worker


def run_job(args):
  file_id, file_name, mime_type = args
  run_file_worker(file_id, file_name, mime_type)


if __name__ == "__main__":

  with DriveService() as drive_service:

    job_params = []

    # Find all folders named INBOX accessible to this service account.
    for inbox in drive_service.find_folders_by_name("INBOX"):

      # Find all files (not folders) in this inbox.
      files = drive_service.list_files_in_folder(inbox["id"])

      job_params.extend([(file["id"], file["name"], file["mimeType"]) for file in files])

    # Run all jobs.
    with Pool(processes=4) as pool:
      pool.map(run_job, job_params)

    print("All jobs have finished. Cleaning up...")
