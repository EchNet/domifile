# installation_commands.py


def define_installation_commands(app):
  """ Retrieve, update, terminate Installations """

  import click
  from flask.cli import with_appcontext

  from db import db
  from managers.InstallationManager import InstallationManager
  from models.Installation import Installation

  #=========================================================================
  # list_installations
  #=========================================================================

  @click.command(name="list_installations")
  @with_appcontext
  @click.argument("include_terminated", required=False)
  def list_installations(include_terminated=False):
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

  #=========================================================================
  # mark_installation_for_termination
  #=========================================================================

  @click.command(name="mark_installation_for_termination")
  @click.argument("ident")
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
