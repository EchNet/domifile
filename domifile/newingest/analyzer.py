
import json
from datetime import date
from typing import List

# --- MOCK: replace with real OpenAI call ---
def create_response(prompt: str) -> str:
  return '{"doc_type":"other","doc_type_confidence":0.5,"document_date":null,"coverage_start":null,"coverage_end":null,"facts":[]}'


def parse_date_safe(s):
  if not s:
    return None
  try:
    y, m, d = s.split("-")
    return date(int(y), int(m), int(d))
  except:
    return None


DOC_TYPES = ["invoice","bank_statement","meeting_minutes","receipt","other"]


def build_chunk_prompt(text: str, filename: str) -> str:
  return f"""
You are a document analyzer.

Rules:
- Return JSON only
- Extract only facts in THIS chunk
- Do not assume global doc_type unless obvious

Filename:
{filename}

Document chunk:
{text}
"""


def build_reduce_prompt(results, filename: str) -> str:
  return f"""
Combine these partial analyses into one final result.

Rules:
- Resolve a single doc_type from allowed values
- Merge dates into document_date / coverage
- Deduplicate facts
- Prefer higher confidence
- Return JSON only

Filename:
{filename}

Partial:
{json.dumps(results)}
"""


def analyze_chunk(text: str, filename: str):
  prompt = build_chunk_prompt(text, filename)
  return json.loads(create_response(prompt))


def reduce_document(results, filename: str):
  prompt = build_reduce_prompt(results, filename)
  return json.loads(create_response(prompt))


def chunk_text(text: str, size=3000):
  for i in range(0, len(text), size):
    yield text[i:i+size]


def analyze_document(document):
  chunks = list(chunk_text(document["text"]))[:20]

  results = [analyze_chunk(c, document["filename"]) for c in chunks]

  final = reduce_document(results, document["filename"])

  document["doc_type"] = final.get("doc_type")
  document["doc_type_confidence"] = final.get("doc_type_confidence")
  document["document_date"] = parse_date_safe(final.get("document_date"))
  document["coverage_start"] = parse_date_safe(final.get("coverage_start"))
  document["coverage_end"] = parse_date_safe(final.get("coverage_end"))

  return final.get("facts", [])
