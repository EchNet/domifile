# manager.py
#
# Manage the continuation or termination of the service for one or all installations.
#
# See to it that for each active installation, its inbox exists and there is a watcher on it.
#
# Depends on the Installation database entity.
#


def update_all_installations():
  print("update all installations")


def update_one_inbox(inbox_id):
  print(f"update one inbox {inbox_id}")
