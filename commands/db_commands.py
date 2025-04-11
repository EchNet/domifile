# db_commands.py


def define_db_commands(app):
  """ Database maintenance commands """

  import click
  from flask.cli import with_appcontext

  from db import db

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
