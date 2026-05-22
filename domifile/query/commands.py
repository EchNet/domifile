# domifile/query/commands.py
import click
import json
from flask.cli import with_appcontext

from .service import QueryService


def install_query_commands(app):

  @click.command("answer-question")
  @click.argument("question")
  @with_appcontext
  def answer_question(question):
    """ Answer a question based on knowledge base. """
    result = QueryService().answer_question(question)
    print(json.dumps(result, indent=3))

  app.cli.add_command(answer_question)
