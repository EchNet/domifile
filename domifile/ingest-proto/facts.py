# domifile/ingest/facts.py
import re

from .temporal import parse_date
from domifile.models import ExtractedFact


def extract_facts(db_session, document):
  if document.doc_type == "invoice":
    extract_invoice_facts(db_session, document)

  elif document.doc_type == "bank_statement":
    extract_statement_facts(db_session, document)


AMOUNT_RE = r"\$?\s?(\d+(?:,\d{3})*(?:\.\d{2})?)"


def extract_invoice_facts(db_session, document):
  amounts = re.findall(AMOUNT_RE, document.text)

  if not amounts:
    return

  # pick largest as total (simple heuristic)
  amount = max(float(a.replace(",", "")) for a in amounts)

  fact = ExtractedFact(
      document_id=document.id,
      fact_type="amount",
      nvalue=amount,
      effective_date=document.document_date,
      confidence=0.7,
      source="regex",
  )
  db_session.add(fact)


LINE_RE = r"(\d{1,2}/\d{1,2}/\d{2,4}).+?(-?\$?\d+(?:,\d{3})*(?:\.\d{2})?)"


def extract_statement_facts(db_session, document):
  lines = re.findall(LINE_RE, document.text)

  for dt_str, amt_str in lines:
    dt = parse_date(dt_str)
    amt = float(amt_str.replace("$", "").replace(",", ""))

    fact = ExtractedFact(
        document_id=document.id,
        fact_type="transaction",
        nvalue=amt,
        effective_date=dt,
        confidence=0.6,
        source="line_parse",
    )

    # crude category detection
    if "insurance" in document.text.lower():
      fact.category = "insurance"

    db_session.add(fact)
