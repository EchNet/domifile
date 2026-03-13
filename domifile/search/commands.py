# domifile/search/commands.py
import click
from flask.cli import with_appcontext


def install_search_commands(app):

  from .search import search_chunks, answer_question

  @click.command("search-chunks")
  @click.argument("text")
  @with_appcontext
  def search_chunks(text):
    results = search_chunks(text)
    for r in results:
      print(r.text[:200])

  app.cli.add_command(search_chunks)

  @click.command("answer-question")
  @click.argument("question")
  @with_appcontext
  def answer_the_question(question):
    result = answer_question(question)
    print(result)

  app.cli.add_command(answer_the_question)
