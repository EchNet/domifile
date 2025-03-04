from flask import Flask
from dotenv import load_dotenv
import os

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.secret_key = app.config["SECRET_KEY"]
app.config["DEBUG"] = os.getenv("DEBUG") == "True"
app.config["GOOGLE_CLIENT_ID"] = os.getenv("GOOGLE_CLIENT_ID")
app.config["GOOGLE_CLIENT_SECRET"] = os.getenv("GOOGLE_CLIENT_SECRET")
