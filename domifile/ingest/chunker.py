# domifile/ingest/chunker.py

from domifile.models import Chunk
from domifile.openai_adapter import create_embedding


def chunk_text(text, size=500):
  for i in range(0, len(text), size):
    yield text[i:i + size]


def create_chunks(db_session, document):
  for chunk_text_block in chunk_text(document.text):
    chunk = Chunk(
        document_id=document.id,
        text=chunk_text_block,
        embedding=create_embedding(chunk_text_block),

        # inherit temporal fields
        doc_type=document.doc_type,
        document_date=document.document_date,
        coverage_start=document.coverage_start,
        coverage_end=document.coverage_end,
    )
    db_session.add(chunk)
