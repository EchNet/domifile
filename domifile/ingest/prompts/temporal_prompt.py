# domifile/ingest/prompts/temporal_prompt.py

from ..doctypes import DOMAIN


def build_temporal_prompt(filename, document_text, doc_type):
  return f"""
  You are a document analyzer for the {DOMAIN} domain.

The document you are given to analyze has been classified as:
doc_type = "{doc_type}"

Your task is to scan the document text to form a "temporal profile", which includes:
* The document's date of issue, if given.
* The range of dates that the document covers, if applicable to the doc_type.  The end date is included in the range.

Take the documents's doc_type into account when interpreting dates found in the document.

For example, a bank statement will have a date of issue and a start and end date of the period covered by the statement, usually one month.

A contrasting example: meeting minutes will usually include the date of the meeting.  This one date comprises the range of covered dates.  The date of issue may or may not appear.

A third example: a safety notice from the local municipality will have a date of issue but no range of covered dates, as it is assumed to apply from the date of issue forward.

Rules:
- Return ONLY valid JSON.
- Extract only fields defined in the following schema definition: {{
    "document_date": "iso date string" | null,
    "date_range_start": "iso date string" | null,
    "date_range_end": "iso date string" | null,
    "date_range_confidence": number in 0..100 | null,
    "comment": "string" | null,
  }}
- ALWAYS return dates in ISO format (YYYY-MM-DD).
- The document_date must never be inferred.  If it does not explicitly appear in the document, omit it.
- The date range may be inferred.  Include the confidence percentage.  If the confidence is less than 50, omit the date range fields.
- You may take the document's filename as a hint to the date range but only if supported by the document contents.

Filename:
{filename}

Document text:
{document_text}
"""
