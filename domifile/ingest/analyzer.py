# domifile/ingest/analyzer.py
import json
import logging

from domifile.models import Document
from domifile.openai_adapter import create_response
from .doctypes import DOC_TYPES, DOMAIN, DOC_TYPE_OTHER, DOC_TYPE_UNKNOWN

DOC_TYPE_PROMPT_FORMAT = f"""
You are a document analyzer.  The document domain is {DOMAIN}.

You are given a number of preset document types and their descriptions below.

Document types:
{ "\n".join(["type={}: {}".format(key, value.get("description")) for key, value in DOC_TYPES[DOMAIN].items()])}

Rules:
- Given the document text and the filename, identify the most likely type of the document, favoring the preset document types.  Express a confidence level as a percentage.
- If the type can be identified with better than 50% confidence but is not one of those described below, the type value to return is "{DOC_TYPE_OTHER} (<doc_type>)"
- If the type cannot be identified with better than 50% confidence, the type value to return is "{DOC_TYPE_UNKNOWN}" and confidence is null.
- Return a dictionary of ( "doc_type": "<type>", "doc_type_confidence": <0..100> )

Filename: {{}}

Document text:
{{}}
"""

logger = logging.getLogger(__name__)


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

  @property
  def doc_type_prompt(self):
    return DOC_TYPE_PROMPT_FORMAT.format(self.document.filename, self.document.text)

  def analyze_document(self):
    """ Caller is responsible for managing database session """

    analysis = create_response(self.doc_type_prompt)

    try:
      analysis = json.parse(analysis)
      self.document.doc_type = analysis.get("doc_type")
      self.document.doc_type_confidence = analysis.get("doc_type_confidence")
    except Exception:
      self.document.doc_type = "unknown"
      logger.exception(f"Unexpected error parsing analysis: {analysis}")

    return analysis
