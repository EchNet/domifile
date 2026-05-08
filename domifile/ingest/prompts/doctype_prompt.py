# domifile/ingest/prompts/doctype_prompt.py

from ..doctypes import DOC_TYPES, DOMAIN, DOC_TYPE_OTHER, DOC_TYPE_UNKNOWN


def build_doctype_prompt(filename, document_text):
  return f"""
You are a document analyzer.  The document domain is {DOMAIN}.

You are given a number of preset document types and their descriptions below.

{ "\n".join(["type={}: {}".format(key, value.get("description")) for key, value in DOC_TYPES[DOMAIN].items()])}

Rules:
- Given the document text and the filename, identify the most likely type of the document, favoring the preset document types.
- Express a confidence level as a percentage.  Confidence reflects how strongly the document matches known structural patterns for that type. (As opposed to guess probability).
- Choose EXACTLY ONE doc_type.  Use confidence to break ties.
- If best match is a preset type → use it.
- If best match is not preset and confidence is >= 50% → use "{DOC_TYPE_OTHER} (<doc_type>)"
- If no type reaches 50% confidence → use "{DOC_TYPE_UNKNOWN}", confidence = null.
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
