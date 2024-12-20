from drive_service import DriveService


def run_file_worker(file_id):
  print(f"START process inbox file {file_id}")

  with DriveService() as drive_utils:
    inbox_id = drive_utils.get_parent_folder_ids(file_id)[0]
    print(f"FOUND inbox id {inbox_id}")

  print(f"FINISH process inbox file {file_id}")
