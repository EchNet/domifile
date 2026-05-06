# domifile/models.py

from datetime import datetime, date
from sqlalchemy import (Integer, String, Text, ForeignKey, DateTime, Date, Float, Numeric, JSON)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector


class Base(DeclarativeBase):
  pass


MODEL_VECTOR_SIZE = 1536  # OpenAI dependency

# -------------------------
# Documents
# -------------------------


class Document(Base):
  __tablename__ = "documents"

  # Primary key
  id: Mapped[int] = mapped_column(Integer, primary_key=True)

  # -------------------------
  #
  # -------------------------

  # The Drive ID.
  drive_file_id: Mapped[str] = mapped_column(String, index=True, unique=True, nullable=False)

  # Cached drive file fields.
  filename: Mapped[str] = mapped_column(String)
  mime_type: Mapped[str] = mapped_column(String)

  # Used to determine text freshness
  drive_modified_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))

  # -------------------------
  # Support for text extraction.
  # -------------------------

  # Text extracted from file.
  text: Mapped[str] = mapped_column(Text)

  # Version of extractor module used to extract text.
  text_extractor_version: Mapped[str | None] = mapped_column(String)

  # document.chunks
  chunks: Mapped[list["Chunk"]] = relationship(back_populates="document",
                                               cascade="all, delete-orphan")

  # -------------------------
  # Support for document typing
  # -------------------------

  # One of a number of preset document types.
  # "other" and "unknown" are non-domain-specific.
  doc_type: Mapped[str | None] = mapped_column(String, index=True)

  # A rough certainty percentage that the AI has assigned to its choice of doc_type.
  doc_type_confidence: Mapped[float | None] = mapped_column(Float)

  # Version of logic that arrived at the document type.
  doc_type_analyzer_version: Mapped[str | None] = mapped_column(String)

  # -------------------------
  # Support for temporal profile and fact extraction
  # -------------------------

  # Date on which the document was created.
  document_date: Mapped[date | None] = mapped_column(Date)

  # Range of dates that the document covers.
  date_range_start: Mapped[date | None] = mapped_column(Date)
  date_range_end: Mapped[date | None] = mapped_column(Date)

  fact_analyzer_version: Mapped[str | None] = mapped_column(String)

  # flexible metadata (vendor, unit, etc.)
  attributes: Mapped[dict | None] = mapped_column(JSON)

  # Flag to show completed ingest.
  ingested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

  def to_dict(self):
    return {
        "id": self.id,
        "drive_file_id": self.drive_file_id,
        "filename": self.filename,
        "mime_type": self.mime_type,
        "drive_modified_time": str(self.drive_modified_time),
        "text": self.text,
        "text_extractor_version": self.text_extractor_version,
        "doc_type": self.doc_type,
        "doc_type_confidence": self.doc_type_confidence,
        "doc_type_analyzer_version": self.doc_type_analyzer_version,
        "document_date": self.document_date.isoformat() if self.document_date else None,
        "date_range_start": self.date_range_start.isoformat() if self.date_range_start else None,
        "date_range_end": self.date_range_end.isoformat() if self.date_range_end else None,
        "fact_analyzer_version": self.doc_type_analyzer_version,
        "attributes": self.attributes,
        "ingested_at": str(self.ingested_at),
    }


# -------------------------
# Chunks (RAG)
# -------------------------


class Chunk(Base):
  __tablename__ = "chunks"

  id: Mapped[int] = mapped_column(Integer, primary_key=True)

  document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), index=True)

  text: Mapped[str] = mapped_column(Text)

  embedding: Mapped[list[float]] = mapped_column(Vector(MODEL_VECTOR_SIZE))

  coverage_start: Mapped[date | None] = mapped_column(Date)
  coverage_end: Mapped[date | None] = mapped_column(Date)

  document: Mapped["Document"] = relationship(back_populates="chunks")


# -------------------------
# Extracted Facts (M2 core)
# -------------------------


class ExtractedFact(Base):
  __tablename__ = "extracted_facts"

  id: Mapped[int] = mapped_column(Integer, primary_key=True)

  document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), index=True)

  fact_type: Mapped[str] = mapped_column(String, index=True)
  # examples: 'transaction', 'amount', 'service_date'

  # value fields (one used depending on type)
  nvalue: Mapped[float | None] = mapped_column(Numeric)
  dvalue: Mapped[date | None] = mapped_column(Date)
  tvalue: Mapped[str | None] = mapped_column(String)

  # qualifiers
  category: Mapped[str | None] = mapped_column(String, index=True)
  vendor: Mapped[str | None] = mapped_column(String)

  # critical for time filtering
  effective_date: Mapped[date | None] = mapped_column(Date, index=True)

  confidence: Mapped[float | None] = mapped_column(Float)
  source: Mapped[str | None] = mapped_column(String)
  # 'header', 'table', 'nlp', etc.


# -------------------------
# Doc Type Registry
# -------------------------


class DocTypeRegistry(Base):
  __tablename__ = "doc_type_registry"

  doc_type: Mapped[str] = mapped_column(String, primary_key=True)

  category: Mapped[str | None] = mapped_column(String)

  capabilities: Mapped[list[str] | None] = mapped_column(JSON)
  # ["amount", "transactions", "coverage"]

  primary_date_field: Mapped[str | None] = mapped_column(String)
  # 'coverage_end', 'document_date', etc.

  extraction_hints: Mapped[dict | None] = mapped_column(JSON)


# -------------------------
# Optional (lightweight linking)
# -------------------------


class DocumentRelationship(Base):
  __tablename__ = "document_relationships"

  id: Mapped[int] = mapped_column(Integer, primary_key=True)

  from_document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), index=True)
  to_document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), index=True)

  relationship_type: Mapped[str] = mapped_column(String)
  # 'derived_from', 'related_to'
