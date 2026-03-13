# domifile/main.py

# Load env settings before importing anything.
from dotenv import load_dotenv

load_dotenv()

# Create app, including socketio, and configure it.
from .app import create_app

app = create_app()

if __name__ == "__main__":
  kwargs = {
      "host": app.config.get("HOST", "localhost"),
      "port": app.config.get("PORT"),
      "debug": app.config.get("DEBUG"),
  }

  # Still warnings from werkzeug
  if app.config.get("ENV") == "dev":
    kwargs["allow_unsafe_werkzeug"] = True

  # Start servers
  app.run(**kwargs)
