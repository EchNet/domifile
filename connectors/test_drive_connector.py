from connectors.drive_connector import DriveConnector

TEST_OWNER = "james.echmalian@gmail.com"
TEST_PARENT = "1jKs0QgEF0iz0nA0QNyCM695Z_gwG8Ck1"
TEST_NAME = "TEST"
TEST_CREDS = "./service-acct-creds.json"

# Load service account info from given filename.
with open(TEST_CREDS, "r") as f:
  service_account_info = f.read()


def test_create_folder(client):
  # NOTE: Transfer of file ownership from service account to personal gmail account is not permitted.

  with DriveConnector(service_account_info) as dc:
    folder = dc.create_folder(TEST_NAME, TEST_PARENT, owner=TEST_OWNER)

    try:
      assert folder.name == TEST_NAME
      assert folder.parent_id == TEST_PARENT
      #assert folder.owner == TEST_OWNER    # See above.

      folder = dc.get(folder.id)
      assert folder.name == TEST_NAME
      assert folder.parent_id == TEST_PARENT
      #assert folder.owner == TEST_OWNER    # See above.

    finally:
      try:
        dc.delete_file(folder.id)
      except:
        pass
