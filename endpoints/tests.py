from flask import Flask
import logging
import unittest
from unittest.mock import Mock

from endpoints.general import define_general_endpoints
from endpoints.install import define_install_endpoints
from endpoints.webhook import define_webhook_endpoints


class TestGeneralEndpoints(unittest.TestCase):

  def setUp(self):
    self.app = Flask(__name__)
    define_general_endpoints(self.app)
    self.client = self.app.test_client()
    logging.disable(logging.CRITICAL)

  def tearDown(self):
    logging.disable(logging.NOTSET)

  def test_health_check(self):
    response = self.client.post("/status")
    assert response.status_code == 200
    assert response.json == {"status": "OK"}


class TestInstallEndpoints(unittest.TestCase):

  def setUp(self):
    self.app = Flask(__name__)
    define_install_endpoints(self.app)
    self.client = self.app.test_client()
    logging.disable(logging.CRITICAL)

  def tearDown(self):
    logging.disable(logging.NOTSET)

  def test_create_installation_no_auth(self):
    response = self.client.post("/installation")
    self.assertEqual(response.status_code, 401)
    self.assertEqual(response.json, {"error": "Missing Authorization"})


class TestWebhook(unittest.TestCase):

  def setUp(self):
    self.app = Flask(__name__)
    define_webhook_endpoints(self.app)
    self.client = self.app.test_client()
    logging.disable(logging.CRITICAL)

  def tearDown(self):
    logging.disable(logging.NOTSET)

  def test_webhook_no_headers(self):
    response = self.client.post("/webhook")
    self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
  unittest.main()
