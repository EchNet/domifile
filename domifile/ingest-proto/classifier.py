# domifile/ingest/classifier.py


def classify_document(document):
  text = document.text.lower()

  if "statement" in text:
    document.doc_type = "bank_statement"
    document.doc_type_confidence = 0.8
  elif "invoice" in text:
    document.doc_type = "invoice"
    document.doc_type_confidence = 0.8
  elif "minutes" in text:
    document.doc_type = "meeting_minutes"
    document.doc_type_confidence = 0.8
  else:
    document.doc_type = "unknown"
    document.doc_type_confidence = 0.3
