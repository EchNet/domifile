# domifile/ingest/temporal.py

import re
from datetime import date

DATE_RE = r"\b(\d{1,2}/\d{1,2}/\d{2,4})\b"


def parse_date(s):
  try:
    m, d, y = s.split("/")
    y = int(y)
    if y < 100:
      y += 2000
    return date(int(y), int(m), int(d))
  except:
    return None


def extract_temporal_profile(document):
  matches = re.findall(DATE_RE, document.text)

  dates = [parse_date(m) for m in matches if parse_date(m)]

  if not dates:
    return

  # naive but effective baseline
  document.document_date = max(dates)

  if document.doc_type == "bank_statement":
    document.coverage_start = min(dates)
    document.coverage_end = max(dates)
