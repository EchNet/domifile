# domifile/query/hybrid.py


def fetch_chunks_for_document(document_id, limit=8):
  from domifile.db import db_transaction
  from domifile.models import Chunk

  with db_transaction(Chunk) as db_session:

    sql = text("""
      SELECT d.filename, d.drive_file_id, c.id, c.text, c.embedding
      FROM chunks c
      JOIN documents d ON d.id = c.document_id
      WHERE c.document_id = :document_id
      ORDER BY c.id
      LIMIT :limit
    """)

    return db_session.execute(sql, {
        "document_id": document_id,
        "limit": limit,
    }).fetchall()
