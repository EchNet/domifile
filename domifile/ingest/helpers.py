# domifile/ingest/helpers.py
from sqlalchemy import select, delete
import logging
from datetime import datetime

from domifile.models import Document, Chunk
from domifile.openai_adapter import create_embedding
from domifile.ingest.text import TextExtractor

logger = logging.getLogger(__name__)


class DocumentFinder:

  def __init__(self, db_session):
    self.db_session = db_session

  def document_for_drive_file(self, drive_file):
    return self.document_for_drive_file_id(drive_file.id)

  def document_for_drive_file_id(self, drive_file_id):
    return self.db_session.execute(
        select(Document).where(Document.drive_file_id == drive_file_id)).scalar_one_or_none()


def parse_gdrive_timestamp(gdrive_timestamp):
  normalized_timestamp = gdrive_timestamp.replace("Z", "+00:00")
  return datetime.fromisoformat(normalized_timestamp)


class DocumentHelper:

  def __init__(self, *, db_session, document, drive_file):
    self.db_session = db_session
    self.document = document  # may be None
    self.drive_file = drive_file

  def document_is_up_to_date(self):
    if not self.document:
      return False
    if not self.document.ingested_at:
      logger.debug("document ingest not completed")
      return False
    db_mod_time = self.document.drive_modified_time
    gdrive_mod_time = self.drive_file.modified_time
    if db_mod_time != gdrive_mod_time:
      logger.debug(f"modified times unequal: {db_mod_time}, {gdrive_mod_time}")
      return False
    if self.document.text_extractor_version != TextExtractor.VERSION:
      logger.debug(f"text extractor version {self.document.text_extractor_version} out of date")
      return False
    return True

  def open_document_for_ingest(self, text, text_extractor_version):
    if self.document is None:
      self.document = Document(drive_file_id=self.drive_file.id)
    self.document.text_extractor_version = text_extractor_version
    self.document.filename = self.drive_file.name
    self.document.mime_type = self.drive_file.mime_type
    self.document.drive_modified_time = self.drive_file.modified_time
    self.document.text = text
    self.document.doc_type = None
    self.document.doc_type_confidence = None
    self.document.doc_type_analyzer_version = None
    self.document.document_date = None
    self.document.date_range_start = None
    self.document.date_range_end = None
    self.document.ingested_at = None
    self.db_session.add(self.document)
    return self.document

  def delete_all_chunks(self):
    self.db_session.execute(delete(Chunk).where(Chunk.document_id == self.document.id))

  def create_chunks(self):

    def chunk_text(text, size=300, extra=30):
      for i in range(0, len(text), size):
        yield text[i:i + size]

    for chunk_text_block in chunk_text(self.document.text):
      chunk = Chunk(
          document_id=self.document.id,
          text=chunk_text_block,
          embedding=create_embedding(chunk_text_block),
      )
      self.db_session.add(chunk)
