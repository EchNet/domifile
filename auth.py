import os
from flask import request, jsonify
from functools import wraps
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token


# Helper function to verify Google ID Token
def verify_google_token(token):
  # Verify the token against Google's servers
  google_client_id = os.getenv("GOOGLE_CLIENT_ID")
  if not google_client_id:
    raise ValueError("GOOGLE_CLIENT_ID environment variable is not set!")
  idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), google_client_id)
  return idinfo  # Contains user info like email


# Temporary API key implementation
def verify_api_key(api_key):
  if api_key == "XYZXYZ":
    return {"email": "james.echmalian@gmail.com"}


# Decorator to require authentication for all endpoints
def auth_required(f):

  @wraps(f)
  def auth_decorated_function(*args, **kwargs):
    auth = request.headers.get("Authorization")
    if not auth:
      return jsonify({"error": "Missing Authorization"}), 401

    if auth.startswith("Bearer "):
      token = auth.split("Bearer ")[1]
      user_info = verify_google_token(token)
      if not user_info:
        return jsonify({"error": "Invalid or expired token"}), 401
      request.user = user_info  # Attach user info to the request object
    elif auth.startswith("API-Key"):
      api_key = auth.split("API-Key ")[1]
      user_info = verify_api_key(api_key)
      if not user_info:
        return jsonify({"error": "Invalid API key"}), 401
    else:
      return jsonify({"error": "Missing or invalid token"}), 401

    return f(*args, **kwargs)

  return auth_decorated_function
