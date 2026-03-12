# domifile/db/commands.py
import click
from flask.cli import with_appcontext


def install_db_commands(app):
  """
    Install database-related CLI commands using the new DB registry.

    Usage:
        flask init-db
        flask drop-db --yes
  """

  from .registry import DatabaseRegistry

  @click.command("init-db")
  @with_appcontext
  def init_db_command():
    """Create all registered database tables."""
    click.echo("Creating all database tables...")

    DatabaseRegistry.instance().create_all()

    click.echo("Database initialized.")

  app.cli.add_command(init_db_command)

  @click.command("drop-db")
  @with_appcontext
  @click.option(
      "--yes",
      is_flag=True,
      help="Skip confirmation prompt (dangerous).",
  )
  def drop_all_tables(yes):
    """⚠️ Drop ALL registered tables from ALL configured databases."""
    if not yes:
      click.confirm(
          "⚠️ This will irreversibly delete ALL data from ALL databases. Continue?",
          abort=True,
      )

    DatabaseRegistry.instance().drop_all()

    click.echo("✅ All tables dropped successfully.")

  app.cli.add_command(drop_all_tables)
