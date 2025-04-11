# Bucket.py


class Bucket:

  NO_ACTION = "none"
  CLASSIFY_ACTION = "classify"
  ACTIONS = [
      NO_ACTION,
      CLASSIFY_ACTION,
      "tabulate",
      "broadcast",
  ]

  BUCKET_ACTION_KEY = "dof_action"

  @staticmethod
  def is_bucket(file):
    return file.is_folder and BUCKET_ACTION_KEY in file.properties
