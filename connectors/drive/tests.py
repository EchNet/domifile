import unittest
from unittest.mock import Mock

from connectors.drive.DriveConnector import DriveConnector


class TestDriveConnector(unittest.TestCase):

  def test_hello(self):
    drive_service = Mock()
    connector = DriveConnector(drive_service)
    self.assertEqual(connector.drive_service, drive_service)


if __name__ == "__main__":
  unittest.main()
