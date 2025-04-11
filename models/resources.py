from models.Installation import Installation


class InstallationContext(AppContext):

  def __init__(self, arg):
    if isinstance(arg, (str, int)):
      installation = Installation.get_by_id(id)
    else:
      installation = arg
    if not isinstance(installation, Installation):
      raise ValueError("Argument must be an Installation instance or an integer ID.")
    self.installation = installation

  def get_service_account_info(self):
    """ Override """
    return ServiceAccountInfo.from_json_string(self.installation.service_account_info)
