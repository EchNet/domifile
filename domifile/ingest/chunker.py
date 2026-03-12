# domifile/ingest/chunker.py


def chunk_text(text, size=800, overlap=100):
  chunks = []
  start = 0
  n = len(text)

  while start < n:
    end = start + size
    chunks.append(text[start:end])
    start = end - overlap

  return chunks
