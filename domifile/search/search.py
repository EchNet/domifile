from openai import OpenAI
from sqlalchemy import text

openai = OpenAI()


def answer_question(question):

  from domifile.db import db_transaction
  from domifile.ingest.models import Chunk

  qvec = openai.embeddings.create(model="text-embedding-3-small",
                                  input=question).data[0].embedding

  with db_transaction(Chunk) as db_session:

    sql = text("""
      SELECT d.filename, c.text
      FROM chunks c
      JOIN documents d ON d.id = c.document_id
      ORDER BY c.embedding <=> CAST(:qvec AS vector)
      LIMIT :limit
    """)

    rows = db_session.execute(sql, {"qvec": qvec, "limit": 3}).fetchall()

    context = "\n\n".join(r.text for r in rows)

    sources = {r.filename for r in rows}

  resp = openai.responses.create(model="gpt-4.1-mini",
                                 input=f"""
You are answering questions about condominium documents.

Use ONLY the information in the context.
Do not infer schedules, rules, or patterns not stated in the context.

If the answer is not explicitly stated in the context, say "Not stated in the documents."

When answering:
- Quote the relevant text.
- Identify the document it came from.

Context:
{context}

Question:
{question}
""")

  return {
      "output_text": resp.output_text,
      "sources": list(s for s in sources),
  }
