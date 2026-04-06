# domifile/query/classify.py
import json
from datetime import date

from domifile.openai_adapter import create_response


def classify_query(question):
  """
    {
      "type": "structured | hybrid | rag",
      "fact_type": "transaction | amount | service_date",
      "category": "insurance | (other) | null",
      "time_range": {
        "start": "YYYY-MM-DD | null",
        "end": "YYYY-MM-DD | null"
      }
    }
  """
  today = date.today().isoformat()

  prompt = f"""
Classify the query below for a property management information system.

Return STRICT JSON with fields:

- type: one of ["structured" | "hybrid" | "rag"]
- fact_type: one of ["transaction", "amount", "service_date"] or null
- category: e.g. "insurance", "landscaping", or null

To choose type:
- If the query is asking for a currency amount or a date, the type is "structured". 
  Examples:
    "How much did we pay for insurance in 2025?"
    "When was the irrigation system last serviced?"

- If the query is asking for data plus an explanation or some context, the type is "hybrid".
  Examples:
    "When was the septic system last serviced and what work was done?"
    "How much did we pay for snow removal last season, and was it more than the prior year?"

- Otherwise, the type is "rag".
  Examples:
    "Who occupied unit 6B in 2024?
    "How much coverage does our insurance policy provide in the event of a fire?"

fact_type must be one of:
- "transaction" → payments, money movement, totals
- "service_date" → visits, servicing, inspections
- "amount" → standalone values not tied to transactions

If the query asks for a total or sum, ALWAYS use "transaction".
If unsure, set fact_type=null (do NOT invent new values).

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
