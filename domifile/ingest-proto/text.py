# domifile/ingest/text.py

import csv
import docx
import tempfile
from pdfminer.high_level import extract_text as pdf_extract_text


class TextExtractor:
  """ Responsible for extracting text from documents of various types. """

  def __init__(self, drive_service, drive_file):
    self.drive_service = drive_service
    self.drive_file = drive_file

  def extract_text(self) -> str:
    """ Main entry point  """

    mime_type = self.drive_file.mime_type
    export_mime_type = self._get_export_mime_type(mime_type)
    extract_func = self._get_extract_func(mime_type)
    if not extract_func:
      raise ValueError(f"Unsupported mime type: {mime_type}")

    with tempfile.TemporaryDirectory() as tmpdir:
      path = self.drive_service.download_file(self.drive_file,
                                              tmpdir=tmpdir,
                                              export_mime_type=export_mime_type)
      return extract_func(path)

  @classmethod
  def _get_export_mime_type(cls, mime_type: str) -> str:

    if mime_type == "application/vnd.google-apps.document":
      return "text/plain"

    if mime_type == "application/vnd.google-apps.spreadsheet":
      return "text/csv"

    return None

  @classmethod
  def _get_extract_func(cls, mime_type: str) -> callable:

    if mime_type == "application/pdf":
      return cls._extract_pdf

    if mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
      return cls._extract_docx

    if mime_type == "application/vnd.google-apps.spreadsheet":
      return cls._extract_gsheet

    if mime_type == "text/plain" or mime_type == "application/vnd.google-apps.document":
      return cls._extract_txt

    return None

  @staticmethod
  def _extract_pdf(path: str) -> str:
    return pdf_extract_text(path)

  @staticmethod
  def _extract_docx(path: str) -> str:
    doc = docx.Document(path)
    return "\n".join(p.text for p in doc.paragraphs)

  @staticmethod
  def _extract_gsheet(path: str) -> str:
    text = []
    with open(path, "r", newline="", encoding="utf-8") as f:
      reader = csv.reader(f)
      for row in reader:
        text.append(' '.join(row))

    return '\n'.join(text)

  @staticmethod
  def _extract_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
      return f.read()
