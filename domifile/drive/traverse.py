# domifile/drive/traverse.py

from abc import ABC, abstractmethod
from .service import DriveService


class DriveFileVisitor(ABC):

  @abstractmethod
  def open_drive_folder(self, folder):
    pass

  @abstractmethod
  def visit_drive_file(self, file):
    pass

  @abstractmethod
  def close_drive_folder(self, folder):
    pass


class DriveFileHierarchy:

  def __init__(self, *, drive_service: DriveService = None, visitor: DriveFileVisitor):
    self.drive_service = drive_service or DriveService()
    self.visitor = visitor

  def traverse(self, root_file_id):
    drive_file = self.drive_service.get(root_file_id)
    self._visit_drive_node(drive_file)

  def _visit_drive_node(self, drive_file):
    if drive_file.is_folder:
      self._visit_drive_folder(drive_file)
    else:
      self._visit_drive_file(drive_file)

  def _visit_drive_folder(self, drive_folder):
    self.visitor.open_drive_folder(drive_folder)

    children = self.drive_service.query().children_of(drive_folder.id).list()

    for f in children:
      self._visit_drive_node(f)

    self.visitor.close_drive_folder(drive_folder)

  def _visit_drive_file(self, drive_file):
    self.visitor.visit_drive_file(drive_file)
