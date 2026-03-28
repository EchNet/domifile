# domifile/ingest/helpers.py
from sqlalchemy import select, delete

from domifile.models import Document, Chunk


class DocumentHelper:

  def __init__(self, db_session):
    self.db_session = db_session

  def document_for_drive_file(self, drive_file):
    return self.document_for_drive_file_id(drive_file.id)

  def document_for_drive_file_id(self, drive_file_id):
    return self.db_session.execute(
        select(Document).where(Document.drive_file_id == drive_file_id)).scalar_one_or_none()

  @staticmethod
  def document_is_up_to_date(document, drive_file):
    return (document and document.ingested_at
            and document.drive_modified_time == drive_file.modified_time)

  def open_document_for_ingest(self, document, drive_file, text):
    if document is None:
      document = Document(
          drive_file_id=drive_file.id,
          filename=drive_file.name,
          mime_type=drive_file.mime_type,
      )
    document.drive_modified_time = drive_file.modified_time
    document.ingested_at = None
    document.text = text
    document.doc_type = None
    document.doc_type_confidence = None
    document.document_date = None
    document.coverage_start = None
    document.coverage_end = None
    document.attributes = None
    self.db_session.add(document)
    return document

  def delete_all_chunks(self, document):
    self.db_session.execute(delete(Chunk).where(Chunk.document_id == document.id))
