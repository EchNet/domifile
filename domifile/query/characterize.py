# domifile/query/characterize.py
import json
from datetime import date

from domifile.openai_adapter import create_response
from domifile.ingest.doctypes import DOMAIN


def characterize_question(question):
  """
    You are an expert on managing HOAs and other property-based businesses.

    Analyze a question to narrow down the scope of documents that contain the answers.

    Return value schema:
    {
      "doc_types": [ "invoice | minutes | ...", ... ],
      "date_ranges": [{
        "start": "YYYY-MM-DD | null",
        "end": "YYYY-MM-DD | null"
      }, ... ]
    }
  """

  prompt = f"""
Analyze the question below from the point of view of an expert in {DOMAIN}.

Characterize the question in the following ways:
1.  What type(s) of document are most likely to contain the answer?
2.  What date range(s) does the question refer to?

Return STRICT JSON with the following structure:
    {
      "doc_types": [ "invoice | minutes | ...", ... ],
      "date_ranges": [{
        "start": "YYYY-MM-DD | null",
        "end": "YYYY-MM-DD | null"
      }, ... ]
    }

Available document types are as follows.

If the document type 
If the question does not fit any particular document type, leave the doc_types field empty.

Category:
- If there is mention of a specific vendor or service, set the category correspondingly.

Query is:
{question}
"""

  raw = create_response(prompt)

  try:
    return json.loads(raw)
  except Exception:
    # safe fallback
    return {"type": "rag"}
