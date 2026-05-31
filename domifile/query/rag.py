# domifile/query/rag.py

import json
import numpy as np


def vec(v):
  # Convert the given stored embedding (JSON string or list) into a unit-length numpy
  # vector so cosine similarity reduces to a fast dot product and comparisons remain
  # scale-independent.
  if isinstance(v, str):
    v = json.loads(v)
  a = np.array(v, dtype=float)
  return a / np.linalg.norm(a)  # Normalize


def mmr(query_vec, rows, k=4, lambda_=0.7):
  # Re-rank candidate chunks using Maximal Marginal Relevance (MMR): iteratively selects
  # chunks that maximize λ·similarity_to_query − (1−λ)·similarity_to_already_selected,
  # balancing relevance against redundancy so the retrieved context is both highly relevant
  # and diverse.
  #
  # `rows` is a list of dicts (Fields: `chunk_id`, `embedding`) representing the most
  # relevant document chunks.

  query_vec = vec(query_vec)
  embeddings = {r['chunk_id']: vec(r['embedding']) for r in rows}

  selected = []
  candidates = rows[:]

  while len(selected) < k and candidates:
    best = None
    best_score = -1e9

    for r in candidates:
      embedding = embeddings[r['chunk_id']]
      rel = np.dot(query_vec, embedding)

      div = 0
      if selected:
        div = max(np.dot(embedding, embeddings[s['chunk_id']]) for s in selected)

      score = lambda_ * rel - (1 - lambda_) * div

      if score > best_score:
        best_score = score
        best = r

    selected.append(best)
    candidates.remove(best)

  return selected
