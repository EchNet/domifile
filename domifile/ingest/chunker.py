# domifile/ingest/chunker.py


def chunk_text(text, size=1500, overlap=150):
  chunks = []
  start = 0
  n = len(text)

  while start < n:
    end = start + size
    chunks.append(text[start:end])
    start = end - overlap

  return chunks
