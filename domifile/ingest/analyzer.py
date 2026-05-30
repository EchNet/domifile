# domifile/ingest/analyzer.py
import json
import logging
import re
from datetime import datetime

from domifile.openai_adapter import create_response
from .. import prompts

logger = logging.getLogger(__name__)


class DocumentAnalyzer:
  """
    Analyze Document and update its doc_type and doc_type_confidence.
    Assumptions:
      * Document text is up to date with the file system file.
      * Chunks are up to date with Document text.
      * Chunks are of the size and displacment specified in settings.
  """

  MAX_TEXT_LENGTH = 10000  # The limit on text length included in a prompt.

  def __init__(self, document):
    self.document = document

  def analyze_document(self):
    """
      Drive the analysis of one document and place the results into the 
      Document model object.  The caller is responsible for managing the
      database session
    """
    text = self._prepare_text()
    try:
      self._analyze_for_doc_type(text)
    except Exception:
      self.document.doc_type = "unknown"
      logger.exception(f"Unexpected error analyzing for doc type")

    try:
      self._analyze_for_temporal_profile(text, self.document.doc_type)
    except Exception:
      logger.exception(f"Unexpected error analyzing temporal profile")
      return

  def _prepare_text(self):
    text = self.document.text
    if len(text) <= self.MAX_TEXT_LENGTH:
      return text
    logger.debug(f"   (truncated text to {self.MAX_TEXT_LENGTH} chars)")
    ELLIPSIS = " ... (remaining text omitted)"
    forelen = self.MAX_TEXT_LENGTH - len(ELLIPSIS)
    return f"{text[:forelen]}{ELLIPSIS}"

  def _analyze_for_doc_type(self, text):
    """ Step 1 of analysis: guess at document type """

    # Run the AI
    analysis = prompts.DoctypePrompt().run(filename=self.document.filename, document_text=text)
    logger.debug(analysis)

    # Save results in Document object.
    self.document.doc_type = analysis.get("doc_type")
    self.document.doc_type_confidence = analysis.get("doc_type_confidence")

  def _analyze_for_temporal_profile(self, text, doc_type):
    """ Step 2 of analysis: pick out dates """

    # Run the AI
    analysis = prompts.TemporalProfilePrompt().run(filename=self.document.filename,
                                                   document_text=text,
                                                   doc_type=doc_type)
    logger.debug(analysis)

    # Save results in Document object.
    self.document.document_date = self._get_analysis_date(analysis, "document_date")
    self.document.date_range_start = self._get_analysis_date(analysis, "date_range_start")
    self.document.date_range_end = self._get_analysis_date(analysis, "date_range_end")

  @staticmethod
  def _get_analysis_date(analysis, key):
    dval = analysis.get(key)
    try:
      return dval and datetime.strptime(dval, "%Y-%m-%d")
    except ValueError:
      logger.error(f"{key}: Bad date string {dval}")
    return None
