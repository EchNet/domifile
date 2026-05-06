# domifile/ingest/service.py
import logging
from datetime import datetime

from domifile.drive import DriveService
from domifile.drive.traverse import DriveFileHierarchy, DriveFileVisitor
from domifile.ingest.text import TextExtractor
from domifile.ingest.helpers import DocumentHelper, DocumentFinder
from domifile.ingest.analyzer import DocumentAnalyzer

logger = logging.getLogger(__name__)


class IngestService:
  """ """

  def __init__(self, *, drive_service=None):
    """ """
    self.drive_service = drive_service or DriveService()

  def ingest_drive_hierarchy(self, root_file_id):
    """ MAIN ENTRY POINT """

    class _IngestVisitor(DriveFileVisitor):

      def __init__(self, service):
        self.service = service
        self.folder_stack = []

      def open_drive_folder(self, folder):
        self.folder_stack.append(folder.name)

      def visit_drive_file(self, file):
        logger.debug(f"[FILE] {'/'.join(self.folder_stack + [file.name])} ({file.id})")
        self.service.ingest_drive_file(file)

      def close_drive_folder(self, folder):
        self.folder_stack = self.folder_stack[0:-1]

    logger.debug(f"[Ingest start] {root_file_id}")
    visitor = _IngestVisitor(self)
    DriveFileHierarchy(visitor=visitor).traverse(root_file_id)
    logger.debug(f"[Ingest complete] {root_file_id}")

  @staticmethod
  def _create_db_session():
    from domifile.db.registry import DatabaseRegistry
    from domifile.models import Document

    return DatabaseRegistry.instance().session_for(Document)

  def ingest_drive_file(self, drive_file):
    """ Ingest one file.  May not be a folder. """
    db_session = self._create_db_session()
    try:
      # Query for existing document.
      document = DocumentFinder(db_session=db_session).document_for_drive_file(drive_file)
      document_helper = DocumentHelper(db_session=db_session,
                                       document=document,
                                       drive_file=drive_file)

      # If document is already ingested and up to date, skip.
      if document_helper.document_is_up_to_date():
        logger.debug(f"  → already up to date")
        return

      # Load document text.
      logger.error(f"  → loading")
      try:
        text = TextExtractor(self.drive_service, drive_file).extract_text()
        text = (text or "").strip()
        logger.debug(f"  → \"{text[0:40]}{'...' if len(text) > 40 else ''}\"")
      except TextExtractor.Error as e:  # Usually unsupported MIME type
        text = ""
        logger.debug(f"  → {str(e)}")

      # Ensure document exists, clear ingested fields.
      document = document_helper.open_document_for_ingest(text, TextExtractor.VERSION)
      if document.id:  # Document already exists.
        document_helper.delete_all_chunks()

      if text:
        db_session.flush()  # Make document ID visible to session.
        document_helper.create_chunks()
        db_session.flush()  # Make chunks visible to session.
        # Analyze document for type.
        doc_analyzer = DocumentAnalyzer(document)
        analysis = doc_analyzer.analyze_document()

      # Finish.
      document.ingested_at = datetime.utcnow()
      db_session.commit()
      logger.debug(f"  → done.")
    except Exception as e:
      db_session.rollback()
      raise
    finally:
      db_session.close()

  def clear_drive_hierarchy(self, root_file_id):
    """
      Remove all extracted information for the given drive hierarchy.
    """

    class _ClearIngestVisitor(DriveFileVisitor):

      def __init__(self, db_session):
        self.db_session = db_session
        self.count = 0

      def visit_drive_file(self, file):
        document = DocumentFinder(db_session=self.db_session).document_for_drive_file(file)
        if document:
          self.db_session.delete(document)
          self.db_session.commit()
          self.count += 1

    db_session = self._create_db_session()
    try:
      visitor = _ClearIngestVisitor(db_session)
      logger.debug(f"[CLEAR start] {root_file_id}")
      hierarchy = DriveFileHierarchy(visitor=visitor)
      hierarchy.traverse(root_file_id)
      logger.debug(f"[CLEAR complete] {root_file_id}")
      return visitor.count
    except Exception as e:
      db_session.rollback()
      raise
    finally:
      db_session.close()
