# domifile/query/sources.py

from sqlalchemy import text


def build_sources_from_documents(db, document_ids):
  rows = db.execute(
      text("""
    SELECT id, filename, drive_file_id
    FROM documents
    WHERE id = ANY(:ids)
  """), {
          "ids": document_ids
      }).fetchall()

  return [{
      "id": r.id,
      "label": r.filename,
      "url": f"https://drive.google.com/file/d/{r.drive_file_id}/view"
  } for r in rows]
