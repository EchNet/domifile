# domifile/models.py

from datetime import datetime, date
from sqlalchemy import (Integer, String, Text, ForeignKey, DateTime, Date, Float, Numeric, JSON)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from pgvector.sqlalchemy import Vector


class Base(DeclarativeBase):
  pass


MODEL_VECTOR_SIZE = 1536  # OpenAI dependency

# -------------------------
# Documents
# -------------------------


class Document(Base):
  __tablename__ = "documents"

  id: Mapped[int] = mapped_column(Integer, primary_key=True)

  drive_file_id: Mapped[str] = mapped_column(String, index=True, unique=True, nullable=False)
  filename: Mapped[str] = mapped_column(String)
  mime_type: Mapped[str] = mapped_column(String)

  drive_modified_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
  ingested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

  text: Mapped[str] = mapped_column(Text)

  # --- M2 additions ---

  doc_type: Mapped[str | None] = mapped_column(String, index=True)
  doc_type_confidence: Mapped[float | None] = mapped_column(Float)

  # temporal profile
  document_date: Mapped[date | None] = mapped_column(Date)
  coverage_start: Mapped[date | None] = mapped_column(Date)
  coverage_end: Mapped[date | None] = mapped_column(Date)

  # flexible metadata (vendor, unit, etc.)
  attributes: Mapped[dict | None] = mapped_column(JSON)


# -------------------------
# Chunks (RAG)
# -------------------------


class Chunk(Base):
  __tablename__ = "chunks"

  id: Mapped[int] = mapped_column(Integer, primary_key=True)

  document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), index=True)

  text: Mapped[str] = mapped_column(Text)

  embedding: Mapped[list[float]] = mapped_column(Vector(MODEL_VECTOR_SIZE))

  # --- denormalized for filtering ---
  doc_type: Mapped[str | None] = mapped_column(String, index=True)

  document_date: Mapped[date | None] = mapped_column(Date)
  coverage_start: Mapped[date | None] = mapped_column(Date)
  coverage_end: Mapped[date | None] = mapped_column(Date)


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
