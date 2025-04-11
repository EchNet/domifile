# DriveWatchMixin.py

import logging

from connectors.drive.errors import raise_error_from_http_error

logger = logging.getLogger(__name__)


class DriveWatchMixin:
  """
    Wrapper for Google Drive services related to the file watch mechanism.

    This is a Mixin.  The derived class must provide a .drive_service property referencing
    a Google Drive API client object. 
  """

  def create_watch_channel(self, *, channel_id, file_id, webhook_url):
    """
      Create a watch channel via which notifications of modifications to a given file 
      or folder are sent to the given webhook URL.

      Parameters
        channel_id   (str) A unique string to identify the channel.
        file_id      (str) The drive ID of the source folder
        webhook_url  (str) The URL of the webhook

      Returns
        (str) The resource ID of the watch channel, needed for closing the channel.
    """
    logger.info(f"Watcher: CREATING watch channel channel_id={channel_id}")

    response = self.drive_service.files().watch(fileId=file_id,
                                                body={
                                                    "id": channel_id,
                                                    "type": "web_hook",
                                                    "address": webhook_url,
                                                }).execute()
    resource_id = response["resourceId"]
    print(f"Watcher: CREATED watch channel channel_id={channel_id}, resource_id={resource_id}")
    return resource_id

  def close_watch_channel(self, *, channel_id, resource_id):
    """
      Close a Google Drive watch channel.

      Parameters
        channel_id   (str) A unique string to identify the channel.
        resource_id  (str) The resource ID of watch channel, as returned by create_watch_channel.

      Returns
        None
    """
    print(f"Watcher: CLOSING watch channel resource_id={resource_id}, channel_id={channel_id}")

    try:
      self.drive_service.channels().stop(body={
          "id": channel_id,
          "resourceId": resource_id,
      }).execute()
    except HttpError as error:
      raise_error_from_http_error(error, "Cannot close watch channel {channel_id}")

    print(f"Watcher: CLOSED watch channel")
