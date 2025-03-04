# main.py

from app import app
from commands import define_commands
from endpoints import define_endpoints
from google_auth import define_google_auth
from log import define_logging

define_logging(app)
define_google_auth(app)
define_endpoints(app)
define_commands(app)

if __name__ == "__main__":
  app.run(debug=True, host='0.0.0.0', port=8080)
