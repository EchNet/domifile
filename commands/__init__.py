# commands.py
# Management commands.

from commands.db_commands import define_db_commands
from commands.service_commands import define_service_commands
from commands.installation_commands import define_installation_commands
from commands.bucket_commands import define_bucket_commands


def define_commands(app):

  define_db_commands(app)
  define_service_commands(app)
  define_installation_commands(app)
  define_bucket_commands(app)
  patch_cli_commands(app)


def patch_cli_commands(app):
  for name, cmd in app.cli.commands.items():
    wrap_command_in_safe_invoke(cmd)


def wrap_command_in_safe_invoke(cmd):
  import click
  orig_invoke = cmd.invoke

  def safe_invoke(ctx):
    try:
      return orig_invoke(ctx)
    except Exception as e:
      click.echo(f"Error: {e}", err=True)
      ctx.exit(1)

  cmd.invoke = safe_invoke
  return cmd
