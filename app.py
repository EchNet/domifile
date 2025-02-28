from flask import Flask
from dotenv import load_dotenv
import logging
import os

load_dotenv()

debug = os.getenv("DEBUG") == "True"

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["DEBUG"] = debug

#
# Logging
#
app.logger.setLevel(logging.DEBUG if debug else logging.INFO)
if debug:
  file_handler = logging.FileHandler("debug.log")
  file_handler.setLevel(logging.DEBUG)
  file_handler.setFormatter(
      logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
  app.logger.addHandler(file_handler)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
app.logger.addHandler(console_handler)
