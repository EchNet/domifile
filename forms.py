# forms.py
#
# Form validation utilities.
#
from flask import jsonify


class FormValidator:

  def __init__(self, required_fields, optional_fields=[]):
    self.required_fields = required_fields
    self.optional_fields = optional_fields

  def validate(self, data):
    required_fields = [] + self.required_fields
    valid_fields = self.optional_fields + required_fields
    given_fields = []
    invalid_fields = []
    duplicate_fields = []

    for key in data.keys():
      if not key in valid_fields:
        invalid_fields += [key]
      elif key in given_fields:
        duplicate_fields += [key]
      else:
        required_fields.remove(key)

    for fields, label in [
        (required_fields, "Missing required"),
        (invalid_fields, "Invalid"),
        (duplicate_fields, "Duplicate"),
    ]:
      if fields:
        raise ValueError(
            jsonify(
                {'error': f'{label} field{"s" if len(fields) > 1 else ""}: {", ".join(fields)}'}))
