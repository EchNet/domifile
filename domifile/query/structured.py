# domifile/query/structured.py

from sqlalchemy import text
from domifile.db import db_transaction
from domifile.models import ExtractedFact


def find_event(intent):
  fact_type = intent.get("fact_type")
  category = intent.get("category")
  tr = intent.get("time_range") or {}
  start = tr.get("start")
  end = tr.get("end")

  if not fact_type:
    return None

  with db_transaction(ExtractedFact) as db:

    sql = """
      SELECT *
      FROM extracted_facts
      WHERE fact_type = :fact_type
    """

    params = {"fact_type": fact_type}

    if category:
      sql += " AND category = :category"
      params["category"] = category

    if start:
      sql += " AND effective_date >= :start"
      params["start"] = start

    if end:
      sql += " AND effective_date <= :end"
      params["end"] = end

    sql += " ORDER BY effective_date DESC LIMIT 1"

    row = db.execute(text(sql), params).fetchone()

    return row
