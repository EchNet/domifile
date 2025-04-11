# bucket_commands.py


def define_bucket_commands(app):
  """ Create and update folders, run folder actions. """

  import click
  from flask.cli import with_appcontext

  from db import db
  from managers.InstallationManager import InstallationManager

  #=========================================================================
  # create_bucket
  #=========================================================================

  @click.command(name="create_bucket")
  @click.argument("installation_id")
  @click.argument("name")
  @click.argument("action", required=False)
  @with_appcontext
  def create_bucket(installation_id, name, action=None):
    context = app.create_installation_context(installation_id=installation_id)
    InstallationManager(context).create_bucket(name, action)

  app.cli.add_command(create_bucket)

  #=========================================================================
  # list_buckets
  #=========================================================================

  @click.command(name="list_buckets")
  @click.argument("installation_id", nargs=1)
  @with_appcontext
  def list_buckets():
    """
      List an installation's buckets.
    """
    count = 0
    for bucket in buckets:
      print(bucket)
      count += 1
    if count == 0:
      print("No installations.")

  app.cli.add_command(list_buckets)
