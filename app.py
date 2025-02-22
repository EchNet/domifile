from flask import Flask
from dotenv import load_dotenv
import logging
import os

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["DEBUG"] = os.getenv("DEBUG") == "True"

#
# Logging
#
app.logger.setLevel(logging.INFO)
app.logger.addHandler(logging.FileHandler("app.log"))
