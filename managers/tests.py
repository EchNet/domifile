# managers/tests.py

from unittest.mock import Mock

from managers import define_app_resources
from models.Installation import Installation
from tests.base import db, FlaskDBTestCase


class InstallationContextTestCase(FlaskDBTestCase):
  CREATOR = "creator@ech.net"
  ROOT_FOLDER_ID = "XYZ"
  SERVICE_ACCOUNT_INFO = "{}"

  def setUp(self):
    super().setUp()
    inst = Installation(creator=self.CREATOR,
                        root_folder_id=self.ROOT_FOLDER_ID,
                        service_account_info=self.SERVICE_ACCOUNT_INFO)
    db.session.add(inst)
    db.session.commit()
    self.assertIsNotNone(inst.id)
    self.inst_id = inst.id

  def test_installation_context(self):
    app = Mock()
    define_app_resources(app)
    self.assertIsNotNone(app.create_installation_context)
    installation_context = app.create_installation_context(installation_id=self.inst_id)
    self.assertIsNotNone(installation_context)
    self.assertEqual(installation_context.installation_id, self.inst_id)
    self.assertIsNotNone(installation_context.installation)


"""
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
"""

if __name__ == "__main__":
  unittest.main()
