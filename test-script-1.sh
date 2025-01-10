#!/bin/bash

echo ===============================================================================

python main.py create_tables

python main.py create_installation james.echmalian@gmail.com 1BVzWOyKnQpBxLM43lRW0IVqXTo8o8NWF creds.json

python main.py list_installations

python main.py simulate_webhook 1BVzWOyKnQpBxLM43lRW0IVqXTo8o8NWF

python main.py mark_installation_for_termination 1BVzWOyKnQpBxLM43lRW0IVqXTo8o8NWF

python main.py update_installations

python main.py tear_down
