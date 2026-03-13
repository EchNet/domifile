# domifile/search/Installer.py

# Register search commands


class Installer:

  @classmethod
  def install(cls, app):

    from .commands import install_search_commands

    install_search_commands(app)
