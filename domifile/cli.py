# domifile/cli.py
import click
import sys
import traceback


def patch_cli(app):
  """ Prettify flask management command output. """

  def wrap_command_in_safe_invoke(cmd):
    orig_invoke = cmd.invoke

    def safe_invoke(ctx):
      try:
        return orig_invoke(ctx)
      except Exception as e:
        click.secho(f"Error: {e}", fg="red")
        if app.config.get("VERBOSE"):
          traceback.print_exc()
        ctx.exit(1)

    cmd.invoke = safe_invoke
    return cmd

  for name, cmd in app.cli.commands.items():
    wrap_command_in_safe_invoke(cmd)
