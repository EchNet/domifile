
from models import ExtractedFact

def persist_facts(document_id, facts):
  objs = []
  for f in facts:
    objs.append(ExtractedFact(
      document_id=document_id,
      fact_type=f.get("fact_type"),
      nvalue=f.get("nvalue"),
      svalue=f.get("svalue"),
      effective_date=f.get("effective_date"),
      confidence=f.get("confidence", 0.7),
      source="llm"
    ))
  return objs
