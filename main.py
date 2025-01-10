# main.py
#
import sys
from endpoints import run_flask_app
from models import create_tables
from models.api_key import create_api_key, expire_api_key
from managers.commands import (
    create_installation,
    list_installations,
    update_installations,
    mark_installation_for_termination,
    simulate_webhook,
    tear_down,
)


def main():
  try:
    function_name = sys.argv[1]
    args = sys.argv[2:]
  except:
    print("Usage: python main.py <function_name> <args_if_applicable>")
    sys.exit(1)

  if function_name in globals() and callable(globals()[function_name]):
    globals()[function_name](*args)
  else:
    print(f"Error: Function '{function_name}' is not defined.")
    sys.exit(1)


if __name__ == "__main__":
  main()
