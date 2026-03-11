import pathlib
from pdfminer.high_level import extract_text as pdf_extract_text
import docx

SUPPORTED_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
}


class TextExtractor:

  @staticmethod
  def extract(path: str, mime_type: str) -> str:
    """
    Extract text from a document.
    """

    if mime_type == "application/pdf":
      return TextExtractor._extract_pdf(path)

    if mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
      return TextExtractor._extract_docx(path)

    if mime_type == "text/plain":
      return TextExtractor._extract_txt(path)

    raise ValueError(f"Unsupported mime type: {mime_type}")

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
