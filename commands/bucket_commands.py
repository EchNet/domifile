# bucket_commands.py


def define_bucket_commands(app):
  """ Create and update folders, run folder actions. """

  import click
  import json
  from flask.cli import with_appcontext

  from db import db
  from managers.Bucket import Bucket
  from managers.BucketManager import BucketManager
  from managers.InstallationBucketManager import InstallationBucketManager
  from managers.PatternManager import PatternManager
  from models.Installation import Installation

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
    InstallationBucketManager(context).create_bucket(name, action=action)

  app.cli.add_command(create_bucket)

  #=========================================================================
  # apply_installation_pattern
  #=========================================================================

  @click.command(name="apply_installation_pattern")
  @click.argument("pattern_json_path")
  @click.argument("installation_id")
  @with_appcontext
  def apply_installation_pattern(pattern_json_path, installation_id):
    context = app.create_installation_context(installation_id=installation_id)
    PatternManager(pattern_json_path).apply_to_installation(context)

  app.cli.add_command(apply_installation_pattern)

  #=========================================================================
  # list_buckets
  #=========================================================================

  @click.command(name="list_buckets")
  @click.argument("installation_id", nargs=1)
  @with_appcontext
  def list_buckets(installation_id):
    """
      List an installation's buckets.
    """
    context = app.create_installation_context(installation_id=installation_id)
    buckets = InstallationBucketManager(context).list_buckets()
    if not buckets:
      print("No buckets.")
    else:
      for bucket in buckets:
        print(bucket)

  app.cli.add_command(list_buckets)

  #=========================================================================
  # upload_file_to_bucket
  #=========================================================================

  @click.command(name="upload_file_to_bucket")
  @click.argument("file_path")
  @click.argument("installation_id")
  @click.argument("bucket_name")
  @with_appcontext
  def upload_file_to_bucket(file_path, installation_id, bucket_name):
    context = app.create_bucket_context(installation_id=installation_id, bucket_name=bucket_name)
    uploaded = context.drive_connector.upload_file(file_path, parent=context.bucket)
    print(f"Uploaded: {uploaded}")

  app.cli.add_command(upload_file_to_bucket)

  #=========================================================================
  # run_bucket_action
  #=========================================================================

  @click.command(name="run_bucket_action")
  @click.argument("installation_id")
  @click.argument("bucket_name")
  @with_appcontext
  def run_bucket_action(installation_id, bucket_name):
    context = app.create_bucket_context(installation_id=installation_id, bucket_name=bucket_name)
    BucketManager(context).run_bucket_action()

  app.cli.add_command(run_bucket_action)
