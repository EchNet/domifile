import re
import json
import secrets


def generate_token(length=24):
  return secrets.token_urlsafe(length)


def validate_email(email):
  pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
  if not re.match(pattern, email):
    raise ValueError(f"Invalid email address: {email}")
  return email


def validate_drive_file_id(file_id):
  """ Validate Google Drive file IDs based on pattern assumptions."""
  pattern = r"^[a-zA-Z0-9_-]{25,60}$"
  if not re.match(pattern, file_id):
    raise ValueError(f"Invalid Drive file ID: {file_id}")
  return file_id


def validate_json(json_string):
  """Validate that a string is proper JSON."""
  try:
    json.loads(json_string)
  except json.JSONDecodeError as e:
    raise ValueError(f"Invalid JSON: {e.msg} at line {e.lineno}, column {e.colno}") from e
  return json_string


def strip_json_markers(text):
  if text.startswith("```json"):
    text = text[len("```json"):].lstrip()
  if text.endswith("```"):
    text = text[:-len("```")].rstrip()
  return text
