# domifile/query/__init__.py
import json
import logging
from datetime import date

from domifile.db import db_transaction
from domifile.models import ExtractedFact
from domifile.openai_adapter import create_response
from .classify import classify_query
from .rag import answer_rag
from .sources import build_sources_from_documents
from .structured import find_event
from .hybrid import fetch_chunks_for_document

logger = logging.getLogger("query")


def answer_question(question):
  logger.debug(f"answer_question {question}")

  intent = classify_query(question)
  logger.debug(f"classified as {json.dumps(intent)}")

  if intent["type"] == "structured":
    result = answer_structured(question, intent)
    logger.debug(f"structured result: {json.dumps(result)}")
    if "answer" in result:
      return result

  if intent["type"] == "hybrid":
    result = answer_hybrid(question, intent)
    logger.debug(f"hybrid result: {json.dumps(result)}")
    if "answer" in result:
      return result

  return answer_rag(question)  # fallback


def answer_structured(question, intent):

  with db_transaction(ExtractedFact) as db:
    row = db.execute(
        text("""
      SELECT *
      FROM extracted_facts
      WHERE fact_type = :type
      ORDER BY effective_date DESC
      LIMIT 1
    """), {
            "type": intent.get("event_type", "visit")
        }).fetchone()

    if not row:
      return {}

    sources = build_sources_from_documents(db, [row.document_id])

    # build answer based on available fields
    if row.amount is not None and row.effective_date:
      answer = f"{event_type} of {row.amount} on {row.effective_date}"

    elif row.effective_date:
      answer = f"{event_type} on {row.effective_date}"

    elif row.amount is not None:
      answer = f"{event_type} amount {row.amount}"

    else:
      answer = f"{event_type} record found"

    return {"answer": answer, "sources": sources}


def answer_hybrid(question, intent):
  event = find_event(intent)

  if not event:
    return {}

  chunks = fetch_chunks_for_document(event.document_id)

  context = "\n\n".join(f"[{c.id}] {c.text}" for c in chunks)

  prompt = f"""
Answer using the context.

Context:
{context}

Question:
{question}
"""

  answer = create_response(prompt)

  # optional: reuse RAG citation helpers later

  with db_transaction(...) as db:
    sources = build_sources_from_documents(db, [event.document_id])

  return {"answer": answer, "sources": sources, "citations": []}
