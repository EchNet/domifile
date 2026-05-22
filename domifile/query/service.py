# domifile/ingest/service.py

import logging

from sqlalchemy import text

from domifile import prompts
from domifile.db import db_transaction
from domifile.models import Chunk
from domifile.openai_adapter import create_embedding

logger = logging.getLogger(__name__)


class QueryService:
  """ """

  def __init__(self, options={}):
    self.options = options

  def answer_question(self, question):
    """ Get a question answered by the AI based on document contents. """
    logger.debug(f"answer_question {question}")

    # Find documents that are likely to have answers.
    # Does the question call for a specific doc type and/or refer to a particular
    # span of time?  If so, filter out unrelated documents.
    filters = prompts.CharacterizeQuestionPrompt().run(question=question)
    doc_types = filters.get("doc_types")
    date_ranges = filters.get("date_ranges")
    logger.debug(f"doc_types={doc_types} date_ranges={date_ranges}")
    date_range_start = date_ranges[0].get("start") if date_ranges else None
    date_range_end = date_ranges[0].end if date_ranges else None

    # Convert the question into multiple compact retrieval-oriented search strings
    search_strings = prompts.QueryPlannerPrompt().run(question=question)
    logger.debug(f"search strings={search_strings}")
    qvecs = [create_embedding(ss) for ss in search_strings]

    with db_transaction(Chunk) as db_session:

      for qvec in qvecs:
        # Build the SQL query.
        where = []
        params = {
            "qvec": qvec,
            "limit": 8,
        }

        if doc_types:
          where.append("d.doc_type = ANY(:doc_types)")
          params["doc_types"] = doc_types

        if date_range_start:
          where.append("(d.date_range_end IS NULL OR d.date_range_end >= :date_range_start)")
          params["date_range_start"] = date_range_start

        if date_range_end:
          where.append("(d.date_range_start IS NULL OR d.date_range_start <= :date_range_end)")
          params["date_range_end"] = date_range_end

        where_sql = f"WHERE {' AND '.join(where)}" if where else ""

        sql = text(f"""
          SELECT d.filename, d.drive_file_id, c.id, c.text, c.embedding
          FROM chunks c
          JOIN documents d ON d.id = c.document_id
          {where_sql}
          ORDER BY c.embedding <=> CAST(:qvec AS vector)
          LIMIT :limit
        """)

        rows = db_session.execute(sql, params).fetchall()
        for filename, drive_file_id, chunk_id, text_value, embedding in rows:
          logger.debug(f"filename={filename} text={text_value[:30]}")

      return {
          "answer": "no clue",
          "sources": [],
      }
      """
    unique_chunks = {c.id: c for c in all_chunks}
    chunks = list(unique_chunks.values())
    qvec = create_embedding(question)
    chunks = mmr(qvec, chunks, k=4)
    all_chunks.extend(chunks)
    return chunks
      prompt = create_prompt(chunks, question)
      answer = create_response(prompt)

      answer = normalize_citations(answer)
      cited_ids = extract_cited_ids(answer)
      sources = build_sources(chunks, cited_ids)
  """
