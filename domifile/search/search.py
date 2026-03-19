import logging
import json
import numpy as np
from sqlalchemy import text

from ..openai_adapter import create_embedding, create_response


def create_planner_prompt(question: str) -> str:
  return (f"""
Expand the user question into 4 short search queries.  The domain is property management.

Rules:
- short phrases
- no punctuation
- no full sentences
- capture different ways the info may appear

Question:
{question}
""")


def plan_queries(question: str) -> list[str]:
  prompt = create_planner_prompt(question)
  output_text = create_response(prompt)
  lines = output_text.strip().split("\n")
  queries = [l.strip("- ").strip() for l in lines if l.strip() and len(l.strip()) > 3]
  return queries[:4]


def fetch_relevant_chunks(qvec):
  from domifile.db import db_transaction
  from domifile.models import Chunk

  with db_transaction(Chunk) as db_session:

    sql = text("""
      SELECT d.filename, d.drive_file_id, c.id, c.text, c.embedding
      FROM chunks c
      JOIN documents d ON d.id = c.document_id
      ORDER BY c.embedding <=> CAST(:qvec AS vector)
      LIMIT :limit
    """)

    chunks = db_session.execute(sql, {"qvec": qvec, "limit": 12}).fetchall()
    return chunks


def vec(v):
  if isinstance(v, str):
    v = json.loads(v)
  a = np.array(v, dtype=float)
  return a / np.linalg.norm(a)  # Normalize


def mmr(query_vec, rows, k=4, lambda_=0.7):
  query_vec = vec(query_vec)
  embeddings = {r.id: vec(r.embedding) for r in rows}

  selected = []
  candidates = rows[:]

  while len(selected) < k and candidates:
    best = None
    best_score = -1e9

    for r in candidates:
      embedding = embeddings[r.id]
      rel = np.dot(query_vec, embedding)

      div = 0
      if selected:
        div = max(np.dot(embedding, embeddings[s.id]) for s in selected)

      score = lambda_ * rel - (1 - lambda_) * div

      if score > best_score:
        best_score = score
        best = r

    selected.append(best)
    candidates.remove(best)

  return selected


def select_chunks(question):
  queries = plan_queries(question)

  all_chunks = []

  for q in queries:
    qvec = create_embedding(q)
    chunks = fetch_relevant_chunks(qvec)
    all_chunks.extend(chunks)

  unique_chunks = {c.id: c for c in all_chunks}
  chunks = list(unique_chunks.values())

  qvec = create_embedding(question)
  chunks = mmr(qvec, chunks, k=4)
  return chunks


def create_context(question):
  chunks = select_chunks(question)
  formatted_chunks = [
      f"{c.text}\n\n- Source: [{c.filename}](https://drive.google.com/file/d/{c.drive_file_id}/view)"
      for c in chunks
  ]
  context = "\n\n-----\n\n".join(formatted_chunks)
  return context


def create_prompt(context, question):
  return (f"""
You are answering questions about property management documents.

Use ONLY the information in the context.
Do not infer schedules, rules, or patterns not stated in the context.

If the answer is not explicitly stated in the context, say "Not stated in the documents", but suggest relevant information stated in the context if it exists.

Include the source IDs of all context items that are cited. 

Context:
{context}

Question:
{question}
""")


def answer_question(question):
  context = create_context(question)
  prompt = create_prompt(context, question)
  output_text = create_response(prompt)
  return output_text
