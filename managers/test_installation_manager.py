from app import app
from models.installation import Installation
from managers.installation_manager import InstallationManager

TEST_CREATOR = "james.echmalian@gmail.com"
TEST_ROOT_FOLDER = "1jKs0QgEF0iz0nA0QNyCM695Z_gwG8Ck1"
TEST_CREDS = "./service-acct-creds.json"


def test_create_installation(client):
  with app.app_context():

    # Load service account info from given filename.
    with open(TEST_CREDS, "r") as f:
      service_account_info = f.read()

    # Validate inputs.
    values = {
        "creator": TEST_CREATOR,
        "root_folder_id": TEST_ROOT_FOLDER,
        "service_account_info": service_account_info,
    }

    assert Installation.validate_installation_values(values)

    installation = Installation.create(values)
    assert installation.status == Installation.Status.READY

    InstallationManager(installation).update_watcher()
    assert installation.status == Installation.Status.IN_SERVICE

    installation.update({"status": Installation.Status.MARKED_FOR_TERMINATION})
    InstallationManager(installation).update_watcher()
    assert installation.status == Installation.Status.TERMINATED
