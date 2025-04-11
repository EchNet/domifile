# managers/__init__.py

from db import db
from models.Installation import Installation
from resources import ResourceProvider
from connectors.googleapis import GoogleApisResourceMixin
from connectors.drive import DriveResourceMixin


def define_app_resources(app):

  ADMIN_SERVICE_ACCOUNT_JSON_PATH = "./service-acct-creds.json"

  class AdHocResourceProvider(ResourceProvider, GoogleApisResourceMixin, DriveResourceMixin):
    """
      Gain API permissions to access resources not specific to any installation.
    """

    def get_service_account_json(self):
      with open(self.service_account_json_path, "r") as f:
        return f.read()

  class InstallationResourceProvider(ResourceProvider, GoogleApisResourceMixin,
                                     DriveResourceMixin):
    """
      Gain API permissions to access installation-specific resources.

      Requires initial setting of installation:Installation or installation_id:int.
    """

    def get_installation(self):
      try:
        installation_id = int(self.installation_id)
      except:
        raise ValueError(f"Invalid installation ID: {self.installation_id}")

      installation = db.session.get(Installation, int(self.installation_id))

      if installation is None:
        raise ValueError(f"No such installation: {self.installation_id}")

      return installation

    def get_service_account_json(self):
      return self.installation.service_account_info

  app.admin_context = AdHocResourceProvider(
      service_account_json_path=ADMIN_SERVICE_ACCOUNT_JSON_PATH)

  def create_ad_hoc_context(**kwargs):
    return AdHocResourceProvider(**kwargs)

  app.create_ad_hoc_context = create_ad_hoc_context

  def create_installation_context(**kwargs):
    return InstallationResourceProvider(**kwargs)

  app.create_installation_context = create_installation_context
