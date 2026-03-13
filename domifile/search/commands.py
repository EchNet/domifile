# domifile/search/commands.py
import click
import json
from flask.cli import with_appcontext


def install_search_commands(app):

  from .search import answer_question

  @click.command("answer-question")
  @click.argument("question")
  @with_appcontext
  def answer_the_question(question):
    result = answer_question(question)
    print(json.dumps(result, indent=3))

  app.cli.add_command(answer_the_question)
