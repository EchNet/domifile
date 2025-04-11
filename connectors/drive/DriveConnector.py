# DriveConnector.py

from connectors.drive.DriveCreateMixin import DriveCreateMixin
from connectors.drive.DriveQueryMixin import DriveQueryMixin
from connectors.drive.DriveRetrieveMixin import DriveRetrieveMixin
from connectors.drive.DriveUpdateMixin import DriveUpdateMixin
from connectors.drive.DriveDeleteMixin import DriveDeleteMixin


class DriveConnector(DriveCreateMixin, DriveQueryMixin, DriveRetrieveMixin, DriveUpdateMixin,
                     DriveDeleteMixin):
  """
    Google Drive API Connector
  """

  def __init__(self, drive_service):
    self.drive_service = drive_service


if __name__ == "__main__":

  TEST_OWNER = "james.echmalian@gmail.com"
  TEST_PARENT = "1jKs0QgEF0iz0nA0QNyCM695Z_gwG8Ck1"
  TEST_NAME = "TEST"

  dc = DriveConnector()

  print(f"Getting folder {TEST_PARENT}")
  folder = dc.get(TEST_PARENT)
  print(f"Got folder {folder.name}")

  print(f"Listing folder {TEST_PARENT}")
  file_count = 0
  for file in dc.query().children_of(TEST_PARENT).list():
    print(f"  {file.name} ({file.id})")
    file_count += 1

  if file_count > 0:
    first_file = dc.query().children_of(TEST_PARENT).first()
    print(f"Deleting file {first_file.name}")
    dc.delete_file(first_file)
    print(f"Deleted file {first_file.name}")
    file_count -= 1

  fname = f"folder {file_count+1}"
  print(f"Creating folder {fname}")
  folder = dc.create_folder(fname,
                            parent=TEST_PARENT,
                            properties={"--domifile-action": "classify"})
  file_count += 1
  print(f"Created folder {folder}")

  if file_count > 6:
    first_file = dc.query().children_of(TEST_PARENT).list()[5]
    print(f"Trashing file {first_file.name}")
    dc.trash_file(first_file)
    print(f"Trashed file {first_file.name}")

  print(f"What's left:")
  for file in dc.query().children_of(TEST_PARENT).including_trashed().list():
    print(f"  {file}")
