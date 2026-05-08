# domifile/ingest/analyzer.py
import json
import logging
import re
from datetime import datetime

from domifile.openai_adapter import create_response
from .prompts.doctype_prompt import build_doctype_prompt
from .prompts.temporal_prompt import build_temporal_prompt

logger = logging.getLogger(__name__)


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
    prompt = build_doctype_prompt(self.document.filename, self.document.text)

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
