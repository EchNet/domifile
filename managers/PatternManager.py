import json
import jsonschema
from jsonschema import validate

from managers.Bucket import Bucket
from managers.InstallationBucketManager import InstallationBucketManager


class PatternManager:
  """
    Create a set of buckets from a pattern, modeling a type of business, for
    example, an HOA. 
  """

  def __init__(self, filepath):
    """
      Args
        filepath   Path to pattern JSON file
    """

    def load_json(filepath):
      with open(filepath, 'r') as f:
        return json.load(f)

    pattern_data = load_json(filepath)

    pattern_schema = load_json("patterns/schema.json")

    try:
      validate(instance=pattern_data, schema=pattern_schema)
    except jsonschema.exceptions.ValidationError as e:
      raise Exception(f"Schema validation failed.") from e

    self.pattern_data = pattern_data

  def apply_to_installation(self, installation_context):
    for bucket_data in self.pattern_data:
      name = bucket_data.get("name")
      action = bucket_data.get("action", Bucket.NO_ACTION)
      InstallationBucketManager(installation_context).create_bucket(name,
                                                                    action=action,
                                                                    rename_existing=True)
