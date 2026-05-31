# domifile/prompts/characterize_prompt.py

import re

from domifile.domains import PropertyManagementDomain, DocType
from domifile.prompts.base import Prompt


class CharacterizeQuestionPrompt(Prompt):

  def build_prompt(self, **kwargs):
    domain = PropertyManagementDomain()
    question = kwargs['question']

    return f"""
Analyze the question below from the point of view of an expert in {domain.name}.

Characterize the question in the following ways:
1.  Of the types of document listed below, in which are the answers likely to be found?
2.  What date range(s) does the question refer to?

Available document types are as follows.
```
{domain.format_doc_types()}
```

Return STRICT JSON with the following structure:
    {{
      "doc_types": [ "invoice | minutes | ...", ... ],
      "date_ranges": [{{
        "start": "YYYY-MM-DD | null",
        "end": "YYYY-MM-DD | null"
      }}, ... ]
      "category": "insurance" | "septic" | "..."
      "comments": "Optional notes on how you arrived at an analysis."
    }}

Rules:
* Return no more than the three most likely doc types.
* If the question does not fit any particular document type, leave the doc_types field empty.
* If there is mention of a specific vendor or service type, set the category correspondingly.  Otherwise, leave it blank.
* Format results as a JSON string, for example: ```[ "doctype1", "doctype2" ]```  Emit ONLY correct JSON.

Question is:
{question}
"""
