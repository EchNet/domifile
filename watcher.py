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
from file_worker import run_file_worker

if __name__ == "__main__":

  with DriveService() as drive_service:

    file_ids = []

    # Find all folders named INBOX accessible to this service account.
    for inbox in drive_service.find_folders_by_name("INBOX"):

      # Find all files (not folders) in this inbox.
      files = drive_service.list_files_in_folder(inbox["id"])

      file_ids.extend([file["id"] for file in files])

    # Run all jobs.
    with Pool(processes=4) as pool:
      pool.map(run_file_worker, file_ids)

    print("All jobs have finished. Cleaning up...")
