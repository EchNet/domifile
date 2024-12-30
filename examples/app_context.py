from flask import Flask, current_app

# Create a Flask app
app = Flask(__name__)

# Set a configuration value
app.config['MY_SETTING'] = 'some_value'

# Use app.app_context() to push the app context
with app.app_context():
  # Access app-related variables or functions
  print(current_app.name)  # Outputs: __main__
  print(current_app.config['MY_SETTING'])  # Outputs: some_value
