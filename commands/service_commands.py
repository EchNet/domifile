# service_commands.py


def define_service_commands(app):
  """ Service-wide management commands """

  import click
  from flask.cli import with_appcontext

  from db import db
  from managers.ServiceManager import ServiceManager

  #=========================================================================
  # create_installation
  #=========================================================================

  @click.command(name="create_installation")
  @click.argument("creator")
  @click.argument("root_folder_id")
  @click.argument("service_account_filename")
  @with_appcontext
  def create_installation(creator, root_folder_id, service_account_filename):
    print(f"Create installation for {creator}, {root_folder_id}")
    installation = ServiceManager.create_installation(creator, root_folder_id,
                                                      service_account_filename)
    print(f"Created installation {installation.id}")

  app.cli.add_command(create_installation)

  #=========================================================================
  # maintain_service
  #=========================================================================

  @click.command(name="maintain_service")
  @with_appcontext
  def maintain_service():
    """
      Run a service-wide watcher update.  For each installation, either start, continue,
      or terminate its watcher, depending on the installation's status.
    """
    print("maintain service START")
    ServiceManager.maintain_service()
    print("maintain service END")

  app.cli.add_command(maintain_service)

  #=========================================================================
  # terminate_service
  #=========================================================================

  @click.command(name="terminate_service")
  @with_appcontext
  def terminate_service():
    """
      Terminate and delete all installations.
    """
    if app.config["ENV"] == "production":
      print("Are you sure?  If yes, re-run the command with -f")
      return

    print("terminate service START")
    ServiceManager.terminate_service()
    print("terminate service END")

  app.cli.add_command(terminate_service)
