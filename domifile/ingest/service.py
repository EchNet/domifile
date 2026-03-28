# domifile/ingest/service.py
import logging
from datetime import datetime

from domifile.db.registry import DatabaseRegistry
from domifile.models import Document
from domifile.drive import DriveService
from domifile.drive.traverse import DriveFileHierarchy, DriveFileVisitor
from domifile.ingest.text import TextExtractor
from domifile.ingest.helpers import DocumentHelper
from domifile.ingest.chunker import create_chunks
from domifile.ingest.temporal import extract_temporal_profile
from domifile.ingest.classifier import classify_document
from domifile.ingest.facts import extract_facts

logger = logging.getLogger(__name__)


class _IngestVisitor(DriveFileVisitor):

  def __init__(self, service):
    self.service = service

  def open_drive_folder(self, folder):
    logger.debug(f"[FOLDER OPEN] {folder.name} ({folder.id})")

  def visit_drive_file(self, file):
    logger.debug(f"[FILE] {file.name} ({file.id})")
    try:
      self.service.ingest_drive_file(file)
    except Exception as e:
      logger.error(f"  → ERROR: {e}")
      raise

  def close_drive_folder(self, folder):
    logger.debug(f"[FOLDER CLOSE] {folder.name} ({folder.id})")


class IngestService:
  """ """

  def __init__(self, *, drive_service=None):
    self.drive_service = drive_service or DriveService()
    self.db_session = DatabaseRegistry.instance().session_for(Document)

  def ingest_drive_hierarchy(self, root_file_id):
    """ MAIN ENTRY POINT """

    hierarchy = DriveFileHierarchy(visitor=_IngestVisitor(self))
    try:
      logger.debug(f"[Ingest start] {root_file_id}")
      hierarchy.traverse(root_file_id)
      logger.debug(f"[Ingest complete] {root_file_id}")
    except Exception as e:
      logger.exception("FATAL ERROR")

  def ingest_drive_file(self, drive_file):
    """ Ingest one file.  May not be a folder. """
    try:
      # Query for existing document.
      document_helper = DocumentHelper(self.db_session)
      document = document_helper.document_for_drive_file(drive_file)

      # If document is already ingested, skip.
      if document_helper.document_is_up_to_date(document, drive_file):
        logger.debug(f"  → already up to date")
        return

      # Load document text.
      logger.error(f"  → loading")
      try:
        text = TextExtractor(self.drive_service, drive_file).extract_text()
      except ValueError as e:
        logger.debug(f"  → skipped - {str(e)}")
        return
      if text is None or not text.strip():
        logger.debug(f"  → skipped - empty text")
        return

      # Ensure document exists, clear ingested fields.
      document = document_helper.open_document_for_ingest(document, drive_file, text)
      self.db_session.flush()  # Create document ID
      document_helper.delete_all_chunks(document)

      # Run extractors.
      logger.error(f"  → extracting")
      create_chunks(self.db_session, document)
      classify_document(document)
      extract_temporal_profile(document)
      extract_facts(self.db_session, document)
      document.ingested_at = datetime.utcnow()
      self.db_session.commit()
      logger.debug(f"  → done.")
    except Exception as e:
      self.db_session.rollback()
      raise

  def close(self):
    db_session = self.db_session
    self.db_session = None
    if db_session:
      try:
        db_session.close()
      except Exception as e:
        pass
