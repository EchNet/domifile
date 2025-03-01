# commands.py
# Management commands.


def define_commands(app):

  import click
  from flask.cli import with_appcontext
  from pprint import pp

  from db import db
  from managers.service_manager import ServiceManager
  from managers.installation_manager import InstallationManager
  from models.installation import Installation

  ####################################################
  # Database maintenance
  ####################################################

  @click.command(name="create_db")
  @with_appcontext
  def create_db():
    db.create_all()
    print(f"Created db.")

  app.cli.add_command(create_db)

  @click.command(name="drop_db")
  @with_appcontext
  def drop_db():
    db.drop_all()
    print(f"Dropped db.")

  app.cli.add_command(drop_db)

  ####################################################
  # Service
  ####################################################

  @click.command(name="update_all_installations")
  @with_appcontext
  def update_all_installations():
    """
      Run a service-wide watcher update.  For each installation, either start, continue,
      or terminate its watcher, depending on the installation's status.
    """
    print("update service")
    ServiceManager.update_all_installations()

  app.cli.add_command(update_all_installations)

  @click.command(name="tear_down_all_installations")
  @with_appcontext
  def tear_down_all_installations():
    """
      Terminate and delete all installations.
    """
    print("tear down all START")

    installations = Installation.query.all()
    for installation in installations:
      print(
          f"{installation.id} {installation.creator} {installation.root_folder_id} {installation.status}"
      )
      if installation.status == Installation.Status.READY:
        installation.update(dict(status=Installation.Status.TERMINATED))
      elif installation.status == Installation.Status.IN_SERVICE:
        installation.update(dict(status=Installation.Status.MARKED_FOR_TERMINATION))
      # Close watchers as needed.
      InstallationManager(installation).update_watcher()

    db.session.query(Installation).delete()
    db.session.commit()

    print("tear down all DONE")

  app.cli.add_command(tear_down_all_installations)

  ####################################################
  # Installations
  ####################################################

  @click.command(name="create_installation")
  @click.argument("creator", nargs=1)
  @click.argument("root_folder_id", nargs=1)
  @click.argument("service_account_filename", nargs=1)
  @with_appcontext
  def create_installation(creator, root_folder_id, service_account_filename):
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

  app.cli.add_command(create_installation)

  @click.command(name="list_installations")
  @with_appcontext
  @click.argument("include_terminated", nargs=-1)
  def list_installations(include_terminated=True):
    """
      List installations.  By default, include terminated installations.

      Parameters:
        include_terminated (bool): True to include terminated installations.
    """
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

  app.cli.add_command(list_installations)

  @click.command(name="mark_installation_for_termination")
  @click.argument("ident", nargs=1)
  @with_appcontext
  def mark_installation_for_termination(ident):
    """
      Mark an installation for termination.  The next update will terminate it.
    """
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

  app.cli.add_command(mark_installation_for_termination)

  @click.command(name="run_inbox_worker")
  @click.argument("ident", nargs=1)
  @with_appcontext
  def run_inbox_worker(ident):
    print(f"Run inbox worker on {ident}")
    installation = Installation.query.get(ident) or Installation.get_by_root_folder_id(ident)
    if installation:
      InstallationManager(installation).run_inbox_worker()
    else:
      print("No such installation.")

  app.cli.add_command(run_inbox_worker)
