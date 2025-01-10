# commands.py
#
# Management commands.
#
from flaskapp import flaskapp as app, db
from models import Installation
from managers.installation_manager import InstallationManager
from managers.service_manager import ServiceManager


def create_installation(creator, root_folder_id, service_account_filename):
  """
  """
  with app.app_context():
    print(f"Create installation for {creator}, {root_folder_id}")

    # Load service account info from given filename.
    with open(service_account_filename, "r") as f:
      service_account_info = f.read()

    # Validate inputs.
    values = Installation.validate_installation_values({
        "creator":
        creator,
        "root_folder_id":
        root_folder_id,
        "service_account_info":
        service_account_info,
    })

    # Check for existing installation for this root folder.
    installation = Installation.get_by_root_folder_id(root_folder_id)
    if installation:
      # Already exists. Reuse the Installation object.  This means that if the installation is
      # marked for termination, push it back into "in service" state, so that its watcher is
      # refreshed.
      print(f"Reusing Installation object {installation}")
      if installation.status in (Installation.Status.MARKED_FOR_TERMINATION,
                                 Installation.Status.TERMINATED, Installation.Status.BLOCKED):
        installation.status = Installation.Status.IN_SERVICE
      installation.creator = values["creator"]
      installation.service_account_info = values["service_account_info"]
    else:
      # Create new Installation.
      print("Creating new Installation object")
      installation = Installation.create(values)

    # Create / cancel and recreate the watcher.
    InstallationManager(installation).update_watcher()
    return installation


def update_installations():
  """
    Run a service-wide watcher update.  For each installation, either start, continue,
    or terminate its watcher, depending on the installation's status.
  """
  with app.app_context():
    print("update all installations")
    ServiceManager.update_all_installations()


def list_installations(include_terminated=True):
  """
    List installations.  By default, include terminated installations.

    Parameters:
      include_terminated (bool): True to include terminated installations.
  """
  with app.app_context():
    if include_terminated:
      installations = Installation.query.all()
    else:
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
def mark_installation_for_termination(ident):
  """
    Mark an installation for termination.  The next update will terminate it.
  """
  with app.app_context():
    installation = Installation.query.get(ident) or Installation.get_by_root_folder_id(ident)
    if installation:
      if installation.status == Installation.Status.MARKED_FOR_TERMINATION:
        print("Installation is already marked for termination")
      elif installation.status == Installation.Status.TERMINATED:
        print("Installation is already terminated")
      else:
        print("Marked installation for termination.")
        installation.update(dict(status=Installation.Status.MARKED_FOR_TERMINATION))
    else:
      print("No such installation.")


def simulate_webhook(ident):
  """
  """
  with app.app_context():
    print(f"Simulate inbox action on {ident}")
    installation = Installation.query.get(ident) or Installation.get_by_root_folder_id(ident)
    if installation:
      InstallationManager(installation).run_inbox_worker()
    else:
      print("No such installation.")


def tear_down():
  """
    Terminate and delete all installations.
  """
  print("Teardown START")

  with app.app_context():
    installations = Installation.query.all()
    for installation in installations:
      print(
          f"{installation.id} {installation.creator} {installation.root_folder_id} {installation.status}"
      )
      if installation.status == Installation.Status.READY:
        installation.update(dict(status=Installation.Status.TERMINATED))
      elif installation.status == Installation.Status.IN_SERVICE:
        installation.update(dict(Installation.Status.MARKED_FOR_TERMINATION))
      # Close watchers as needed.
      InstallationManager(installation).update_watcher()

    db.session.query(Installation).delete()
    db.session.commit()

  print("Teardown DONE")
