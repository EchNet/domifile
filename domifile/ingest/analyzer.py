# domifile/ingest/analyzer.py
import json
import logging
import re
from datetime import datetime

from domifile.models import Document
from domifile.openai_adapter import create_response
from .doctypes import DOC_TYPES, DOMAIN, DOC_TYPE_OTHER, DOC_TYPE_UNKNOWN

logger = logging.getLogger(__name__)


def build_doc_type_prompt(filename, document_text):
  return f"""
You are a document analyzer.  The document domain is {DOMAIN}.

You are given a number of preset document types and their descriptions below.

{ "\n".join(["type={}: {}".format(key, value.get("description")) for key, value in DOC_TYPES[DOMAIN].items()])}

Rules:
- Given the document text and the filename, identify the most likely type of the document, favoring the preset document types.
- Express a confidence level as a percentage.  Confidence reflects how strongly the document matches known structural patterns for that type (not guess probability).
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


def parse_llm_json(text: str) -> dict:
  text = text.strip()
  # Remove ```json ... ``` or ``` ... ```
  match = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, re.DOTALL)
  if match:
    text = match.group(1).strip()

  return json.loads(text)


class DocumentAnalyzer:
  """
    Analyze Document and update its doc_type and doc_type_confidence.
    Assumptions:
      * Document text is up to date with the file system file.
      * Chunks are up to date with Document text.
      * Chunks are of the size and displacment specified in settings.
  """

  def __init__(self, document):
    self.document = document

  def analyze_document(self):
    """
      Drive the analysis of one document and place the results into the 
      Document model object.  The caller is responsible for managing the
      database session
    """
    try:
      self._analyze_for_doc_type()
    except Exception:
      self.document.doc_type = "unknown"
      logger.exception(f"Unexpected error analyzing for doc type")

    try:
      self._analyze_for_temporal_profile(self.document.doc_type)
    except Exception:
      logger.exception(f"Unexpected error analyzing temporal profile")
      return

  def _analyze_for_doc_type(self):
    """ Step 1 of analysis: guess at document type """

    # Generate prompt.
    prompt = build_doc_type_prompt(self.document.filename, self.document.text)

    # Run the AI
    analysis = create_response(prompt)
    logger.debug(analysis)

    # Save results in Document object.
    analysis = parse_llm_json(analysis)
    self.document.doc_type = analysis.get("doc_type")
    self.document.doc_type_confidence = analysis.get("doc_type_confidence")

  def _analyze_for_temporal_profile(self, doc_type):
    """ Step 2 of analysis: pick out dates """

    # Generate prompt.
    prompt = build_temporal_prompt(self.document.filename, self.document.text, doc_type)

    # Run the AI
    analysis = create_response(prompt)
    logger.debug(analysis)

    # Save results in Document object.
    analysis = parse_llm_json(analysis)
    self.document.document_date = self._get_analysis_date(analysis, "document_date")
    self.document.date_range_start = self._get_analysis_date(analysis, "date_range_start")
    self.document.date_range_end = self._get_analysis_date(analysis, "date_range_start")

  @staticmethod
  def _get_analysis_date(analysis, key):
    dval = analysis.get(key)
    try:
      return dval and datetime.strptime(dval, "%Y-%m-%d")
    except ValueError:
      logger.error(f"{key}: Bad date string {dval}")
    return None
