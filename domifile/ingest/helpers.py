# domifile/ingest/helpers.py
from sqlalchemy import select, delete

from domifile.models import Document, Chunk
from domifile.openai_adapter import create_embedding


class DocumentFinder:

  def __init__(self, db_session):
    self.db_session = db_session

  def document_for_drive_file(self, drive_file):
    return self.document_for_drive_file_id(drive_file.id)

  def document_for_drive_file_id(self, drive_file_id):
    return self.db_session.execute(
        select(Document).where(Document.drive_file_id == drive_file_id)).scalar_one_or_none()


class DocumentHelper:

  def __init__(self, *, db_session, document, drive_file):
    self.db_session = db_session
    self.document = document  # may be None
    self.drive_file = drive_file

  def document_is_up_to_date(self):
    return (self.document and self.document.ingested_at
            and self.document.drive_modified_time == self.drive_file.modified_time)

  def open_document_for_ingest(self, text):
    if self.document is None:
      self.document = Document(
          drive_file_id=self.drive_file.id,
          filename=self.drive_file.name,
          mime_type=self.drive_file.mime_type,
      )
    self.document.drive_modified_time = self.drive_file.modified_time
    self.document.ingested_at = None
    self.document.text = text
    self.document.doc_type = None
    self.document.doc_type_confidence = None
    self.document.document_date = None
    self.document.coverage_start = None
    self.document.coverage_end = None
    self.document.attributes = None
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
