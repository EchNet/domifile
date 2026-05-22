# domifile/prompts/doctype_prompt.py

from domifile.domains import PropertyManagementDomain, DocType
from domifile.prompts.base import Prompt


class DoctypePrompt(Prompt):

  def build_prompt(self, **kwargs):
    domain = PropertyManagementDomain()
    filename = kwargs['filename']
    document_text = kwargs['document_text']

    return f"""
You are an expert in {domain.name}.

Your job is to analyze a document to determine its type.

You are given a number of preset document types and their descriptions below.

```
{domain.format_doc_types()}
```

Rules:
- Given the document text and the filename, identify the most likely type of the document, favoring the preset document types.
- Express a confidence level as a percentage.  Confidence reflects how strongly the document matches known structural patterns for that type. (As opposed to guess probability).
- Choose EXACTLY ONE doc_type.  Use confidence to break ties.
- If best match is a preset type → use it.
- If best match is not preset and confidence is >= 50% → use "{DocType.OTHER.code} (<doc_type>)"
- If no type reaches 50% confidence → use "{DocType.UNKNOWN.code}", confidence = null.
- Return ONLY valid JSON.  No out-of-band commentary.
- Schema: {{
    "doc_type": string,
    "doc_type_confidence": number in 0..100 | null,
    "comments": string | null
  }}

Filename: {filename}

Document text:
{document_text}
"""
