import logging
import os
from openai import OpenAI
from datetime import datetime
from sqlalchemy import select, delete

from ..db import db_transaction
from ..drive import DriveService
from .extractor import TextExtractor
from ..models import Document, Chunk
from .chunker import chunk_text

logger = logging.getLogger(__name__)
openai = OpenAI()


class Ingester:

  def __init__(self):
    self.drive_service = DriveService()

  # Entry point
  def ingest_from_drive(self, drive_file_id):
    with db_transaction(Document) as db_session:
      drive_file = self.drive_service.get(drive_file_id)
      if drive_file.is_folder:
        self._ingest_drive_folder(drive_file, db_session)
      else:
        self._ingest_drive_file(drive_file, db_session)

  def _ingest_drive_folder(self, drive_folder, db_session):
    children = self.drive_service.query().children_of(drive_folder.id).list()
    for f in children:
      if f.is_folder:
        self._ingest_drive_folder(f, db_session)
      else:
        self._ingest_drive_file(f, db_session)

  def _ingest_drive_file(self, drive_file, db_session):
    try:
      if not TextExtractor.is_usable_mime_type(drive_file.mime_type):
        logger.warn(f"Skipping {drive_file.id} - unusable type ({drive_file.mime_type})")
        return

      if self._find_document(drive_file, db_session):
        logger.warn(f"Skipping {drive_file.id} - already ingested")
        return

      text = self._extract_text_from_file(drive_file).strip()
      if text:
        logger.warn(f"Processing {drive_file.id} {drive_file.name}")
        doc = self._upsert_document(db_session, drive_file, text)
        db_session.flush()
        self._chunk_text(text, doc, db_session)
      else:
        logger.warn(f"Skipping {drive_file.id} - NO TEXT")
    except Exception as e:
      logger.exception(f"Error extracting text from {drive_file.id}")
      raise

  @staticmethod
  def _find_document(file, db_session):
    return db_session.query(Document).filter(
        Document.drive_file_id == file.id,
        Document.drive_modified_time == file.modified_time,
    ).one_or_none()

  def _extract_text_from_file(self, f):
    tmp_name = f"/tmp/{f.name}"
    try:
      path = self.drive_service.download_file(f.id, tmp_name)
      text = TextExtractor.extract(path, f.mime_type)
      return text
    finally:
      try:
        os.remove(tmp_name)
      except Exception:
        pass

  def _upsert_document(self, db_session, drive_file, text):
    doc = db_session.execute(
        select(Document).where(Document.drive_file_id == drive_file.id)).scalar_one_or_none()
    if doc is None:
      doc = Document(
          drive_file_id=drive_file.id,
          filename=drive_file.name,
          mime_type=drive_file.mime_type,
          drive_modified_time=drive_file.modified_time,
          ingested_at=datetime.utcnow(),
          text=text,
      )
      db_session.add(doc)
    else:
      if doc.drive_modified_time != drive_file.modified_time:
        doc.filename = drive_file.name
        doc.mime_type = drive_file.mime_type
        doc.drive_modified_time = drive_file.modified_time
        doc.ingested_at = datetime.utcnow()
        doc.text = text

        # Toss old chunks.
        db_session.execute(delete(Chunk).where(Chunk.document_id == document_id))

    return doc

  def _chunk_text(self, text, doc, db_session):
    for c in chunk_text(text):
      embedding = openai.embeddings.create(
          model="text-embedding-3-small",
          input=c,
      ).data[0].embedding
      db_session.add(Chunk(document_id=doc.id, text=c, embedding=embedding))
