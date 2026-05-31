# domifile/ingest/service.py

import logging
import re

from sqlalchemy import text

from domifile import prompts
from domifile.db import db_transaction
from domifile.models import Chunk
from domifile.openai_adapter import create_embedding
from .rag import mmr

logger = logging.getLogger(__name__)


class QueryService:
  """ """

  def __init__(self, options={}):
    self.options = options
    self.max_context_rows = options.get("max_context_rows", 4)

  def answer_question(self, question):
    """ Get a question answered by the AI based on document contents. """
    logger.debug(f"answer_question {question}")

    # Convert the question into multiple compact retrieval-oriented search strings
    search_strings = prompts.QueryPlannerPrompt().run(question=question)
    logger.debug(f"search strings={search_strings}")
    qvecs = [create_embedding(ss) for ss in search_strings]

    # Find documents that are likely to have answers.
    # Does the question imply a specific doc type and/or refer to a particular
    # span of time?  If so, filter out unrelated documents.
    filters = prompts.CharacterizeQuestionPrompt().run(question=question)
    doc_types = filters.get("doc_types")
    date_ranges = filters.get("date_ranges")
    logger.debug(f"doc_types={doc_types} date_ranges={date_ranges}")

    # Retrieve a list of dicts (Fields: filename, drive_file_id, chunk_id, text_value,
    # embedding } representing the most relevant document chunks.
    context_rows = self._get_relevant_chunks(qvecs=qvecs,
                                             doc_types=doc_types,
                                             date_ranges=date_ranges)
    logger.debug(f"found {len(context_rows)} relevant chunk(s)")

    answer, sources = self._answer_the_question(question=question, context_rows=context_rows)

    return {
        "answer": answer,
        "sources": sources,
    }

  def _get_relevant_chunks(self, *, qvecs, doc_types, date_ranges):

    chunks_by_id = {}

    with db_transaction(Chunk) as db_session:

      for qvec in qvecs:
        # Get the semantically relevant chunks for this query string.
        rows = self._select_chunks(
            db_session=db_session,
            qvec=qvec,
            doc_types=doc_types,
            date_ranges=date_ranges,
        )

        # Save results in a list.
        selected_chunks = [{
            "filename": filename,
            "drive_file_id": drive_file_id,
            "chunk_id": chunk_id,
            "text_value": text_value,
            "embedding": embedding,
        } for filename, drive_file_id, chunk_id, text_value, embedding in rows]
        logger.debug(f"selected {len(selected_chunks)} chunk(s)")

        # Re-rank chunks using Maximal Marginal Relevance.
        selected_chunks = mmr(qvec, selected_chunks, k=self.max_context_rows)

        # Uniquify the chunks.
        for c in selected_chunks:
          chunks_by_id[c["chunk_id"]] = c

    return list(chunks_by_id.values())

  def _select_chunks(self, *, db_session, qvec, doc_types, date_ranges):
    # Build an SQL query that filters out irrelevant documents by type and
    # time period, and sorts by semantic proximity to the query keywords,
    # represented by qvec.  Execute the query to get selected chunks.
    where = []
    params = {
        "qvec": qvec,
        "limit": 16,
    }

    if doc_types:
      where.append("d.doc_type = ANY(:doc_types)")
      params["doc_types"] = doc_types

    date_range_start = date_ranges[0].get("start") if date_ranges else None
    date_range_end = date_ranges[0].get("end") if date_ranges else None
    # TODO: support more than one date range.

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

    return db_session.execute(sql, params).fetchall()

  def _answer_the_question(self, *, question, context_rows):
    answer = prompts.AnswerQuestionPrompt().run(question=question, context_rows=context_rows)
    answer = self._normalize_citations(answer)
    cited_ids = self._extract_cited_ids(answer)
    sources = self._build_sources(context_rows, cited_ids)
    return answer, sources

  @staticmethod
  def _normalize_citations(text: str) -> str:
    # remove spaces like [111, 222] → [111,222]
    return re.sub(r'\[\s*([\d,\s]+)\s*\]',
                  lambda m: "[" + ",".join(s.strip() for s in m.group(1).split(",")) + "]", text)

  @staticmethod
  def _extract_cited_ids(text: str) -> list[int]:
    matches = re.findall(r'\[([\d,\s]+)\]', text)

    ids = set()
    for m in matches:
      for part in m.split(","):
        part = part.strip()
        if part.isdigit():
          ids.add(int(part))

    return sorted(ids)

  @staticmethod
  def _build_sources(context_rows, cited_ids):
    by_id = {c['chunk_id']: c for c in context_rows}

    return [{
        "id": cid,
        "label": by_id[cid]['filename'],
        "url": f"https://drive.google.com/file/d/{by_id[cid]['drive_file_id']}/view"
    } for cid in cited_ids if cid in by_id]
