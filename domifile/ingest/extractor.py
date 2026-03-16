import pathlib
from pdfminer.high_level import extract_text as pdf_extract_text
import docx


class TextExtractor:

  @classmethod
  def _get_extract_func(cls, mime_type: str):

    if mime_type == "application/pdf":
      return cls._extract_pdf

    if mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
      return cls._extract_docx

    if mime_type == "text/plain":
      return cls._extract_txt

    return None

  @classmethod
  def is_usable_mime_type(cls, mime_type):
    return cls._get_extract_func(mime_type) is not None

  @classmethod
  def extract(cls, path: str, mime_type: str) -> str:
    extract_func = cls._get_extract_func(mime_type)
    if not extract_func:
      raise ValueError(f"Unsupported mime type: {mime_type}")
    return extract_func(path)

  @staticmethod
  def _extract_pdf(path: str) -> str:
    return pdf_extract_text(path)

  @staticmethod
  def _extract_docx(path: str) -> str:
    doc = docx.Document(path)
    return "\n".join(p.text for p in doc.paragraphs)

  @staticmethod
  def _extract_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
      return f.read()
