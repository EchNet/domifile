# service_manager.py
#
# Manage the continuance or termination of the service for its various installations.
#
# See to it that for each active installation, its folder structure has been created
# and there is a watcher on it.
#
from datetime import datetime, timedelta
from managers.installation_manager import InstallationManager
from models import Installation


class ServiceManager:
  """
    ServiceManager is responsible for maintaining the service as a whole.
  """
  REFRESH_DAYS = 3

  @classmethod
  def update_all_installations(cls):
    three_days_ago = datetime.utcnow() - timedelta(days=cls.REFRESH_DAYS)

    installations = Installation.query.filter(
        # Exclude TERMINATED...
        Installation.status != Installation.Status.TERMINATED,
        # Exclude recently refreshed...
        ~((Installation.status == Installation.Status.IN_SERVICE) &
          (Installation.last_refresh >= three_days_ago))).all()

    for installation in installations:
      InstallationManager(installation).update_watcher()
