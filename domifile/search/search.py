from openai import OpenAI
from sqlalchemy import text

openai = OpenAI()


def search_chunks(question, limit=5):

  from domifile.db import db_transaction
  from domifile.ingest.models import Chunk

  qvec = openai.embeddings.create(model="text-embedding-3-small",
                                  input=question).data[0].embedding

  with db_transaction(Chunk) as db_session:

    sql = text("""
      SELECT text
      FROM chunks
      ORDER BY embedding <=> CAST(:qvec AS vector)
      LIMIT :limit
    """)

    return db_session.execute(sql, {"qvec": qvec, "limit": limit}).fetchall()


def answer_question(question):
  chunks = search_chunks(question, limit=5)

  context = "\n\n".join(c.text for c in chunks)

  resp = openai.responses.create(model="gpt-4.1-mini",
                                 input=f"""
Answer the question using the context below.

Context:
{context}

Question:
{question}
""")

  return resp.output_text
