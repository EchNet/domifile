import json
import numpy as np
from openai import OpenAI
from sqlalchemy import text

openai = OpenAI()


def vec(v):
  if isinstance(v, str):
    v = json.loads(v)
  return np.array(v, dtype=float)


def mmr(query_vec, rows, k=4, lambda_=0.7):
  selected = []
  candidates = rows[:]
  query_vec = vec(query_vec)

  while len(selected) < k and candidates:
    best = None
    best_score = -1e9

    for r in candidates:
      embedding = vec(r.embedding)
      rel = np.dot(query_vec, embedding)

      div = 0
      if selected:
        div = max(np.dot(embedding, vec(s.embedding)) for s in selected)

      score = lambda_ * rel - (1 - lambda_) * div

      if score > best_score:
        best_score = score
        best = r

    selected.append(best)
    candidates.remove(best)

  return selected


def answer_question(question):

  from domifile.db import db_transaction
  from domifile.models import Chunk

  qvec = openai.embeddings.create(model="text-embedding-3-small",
                                  input=question).data[0].embedding

  with db_transaction(Chunk) as db_session:

    sql = text("""
      SELECT d.filename, c.text, c.embedding
      FROM chunks c
      JOIN documents d ON d.id = c.document_id
      ORDER BY c.embedding <=> CAST(:qvec AS vector)
      LIMIT :limit
    """)

    rows = db_session.execute(sql, {"qvec": qvec, "limit": 12}).fetchall()
    rows = mmr(qvec, rows, k=4)

    context = "\n\n".join(r.text for r in rows)

    sources = {r.filename for r in rows}

  resp = openai.responses.create(model="gpt-4.1-mini",
                                 input=f"""
You are answering questions about condominium documents.

Use ONLY the information in the context.
Do not infer schedules, rules, or patterns not stated in the context.

If the answer is not explicitly stated in the context, say "Not stated in the documents", but suggest relevant information stated in the context if it exists.

Context:
{context}

Question:
{question}
""")

  return {
      "output_text": resp.output_text,
      "sources": list(s for s in sources),
  }
