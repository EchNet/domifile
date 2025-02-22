# main.py

from app import app
from commands import define_commands
from endpoints import define_endpoints

define_endpoints(app)
define_commands(app)

if __name__ == "__main__":
  app.run(debug=True, host='0.0.0.0', port=8080)
