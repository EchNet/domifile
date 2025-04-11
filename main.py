# main.py

import os
from dotenv import load_dotenv

from app import create_app

load_dotenv()

env = os.environ.get("FLASK_ENV", "development").lower()

config_map = {
    "development": "DevelopmentConfig",
    "testing": "TestingConfig",
    "staging": "StagingConfig",
    "production": "ProductionConfig",
}

app = create_app(config_map.get(env, "DevelopmentConfig"))

if __name__ == "__main__":
  app.run()
