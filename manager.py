# manager.py
#
# Manage the continuance or termination of the service for its various installations.
#
# See to it that for each active installation, its folder structure has been created
# and there is a watcher on it.
#
# Every installation marked for termination will be terminated.
#
from flaskapp import flaskapp as app
from models import Installation
from watcher import Watcher
from datetime import datetime, timedelta
from connectors.drive_connector import DriveService


class ServiceManager:
  """
    ServiceManager is responsible for maintaining the service as a whole.
  """
  REFRESH_DAYS = 3

  @classmethod
  def update_all_installations(cls):
    print("update all installations")
    three_days_ago = datetime.utcnow() - timedelta(days=cls.REFRESH_DAYS)

    installations = Installation.query.filter(
        Installation.status != Installation.Status.TERMINATED,  # Exclude TERMINATED
        ~((Installation.status == Installation.Status.IN_SERVICE) &
          (Installation.last_refresh >= three_days_ago))  # Exclude recently refreshed
    ).all()

    for installation in installations:
      InstallationManager(installation).update()


class InstallationManager:
  """
    InstallationManager is responsible for one installation.
  """

  @staticmethod
  def for_installation_id(installation_id):
    installation = Installation.query.get(installation_id)
    return InstallationManager(installation)

  def __init__(self, installation):
    self.installation = installation

  def update(self):
    # Continue or terminate this installation as appropriate.
    #
    if installation.status == Installation.Status.READY:
      print("Starting up installation {installation.id}")
      self.invoke_watcher("start")
      installation.update_status(Installation.Status.IN_SERVICE)
    elif installation.status == Installation.Status.IN_SERVICE:
      print("Continuing installation {installation.id}")
      self.invoke_watcher("refresh")
      installation.update_last_refresh()
    elif installation.status == Installation.Status.MARKED_FOR_TERMINATION:
      print("Terminating installation {installation.id}")
      self.invoke_watcher(cancel)
      installation.update_status(Installation.Status.TERMINATED)
    elif installation.status == Installation.Status.TERMINATED:
      print("Installation {installation.id} was already terminated")

  @property
  def inbox_id(self):
    file_structure = self.verify_file_structure()
    return file_structure["inbox_id"]

  def verify_file_structure(self):
    if not self.file_structure:
      pass
    return self.file_structure

  def invoke_watcher(self):
    try:
      inbox_id = self.inbox_id
      watcher = Watcher(inbox_id)
      getattr(watcher, method_name)()
    except Exception as e:
      installation.update_status(Installation.Status.BLOCKED)
      # TODO: log, log, log, email


#
# Management command.
#
def update_all_installations():
  """
  """
  with app.app_context():
    print("update all installations")
    ServiceManager.update_all_installations()


#
# Management command.
#
def list_installations():
  """
  """
  with app.app_context():
    installations = Installation.query.filter(
        Installation.status != Installation.Status.TERMINATED)
    count = 0
    for installation in installations:
      print(
          f"{installation.id} {installation.creator} {installation.root_folder_id} {installation.status}"
      )
      count += 1
    if count == 0:
      print("No installations.")


#
# Management command.
#
def mark_installation_for_termination(installation_id):
  """
  """
  with app.app_context():
    installation = Installation.for_installation_id(installation_id)
    if installation:
      if installation.status == Installation.Status.MARKED_FOR_TERMINATION:
        print("Installation is already marked for termination")
      elif installation.status == Installation.Status.TERMINATED:
        print("Installation is already terminated")
      else:
        print("Marked installation for termination.")
        installation.mark_for_termination()
    else:
      print("No such installation.")


#
# Management command.
#
def update_installation(installation_id):
  """
  """
  with app.app_context():
    installation = Installation.for_installation_id(installation_id)
    if installation:
      installation.update()
    else:
      print("No such installation.")
