# domifile/ingest/models.py

from sqlalchemy import Integer, String, Text, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from pgvector.sqlalchemy import Vector


class Base(DeclarativeBase):
  """Declarative base for Resource."""
  pass


class Document(Base):
  __tablename__ = "documents"

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  drive_file_id: Mapped[str] = mapped_column(String)
  filename: Mapped[str] = mapped_column(String)
  text: Mapped[str] = mapped_column(Text)


MODEL_VECTOR_SIZE = 1536  # OpenAI dependency: text-embedding-3-small


class Chunk(Base):
  __tablename__ = "chunks"

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"))
  text: Mapped[str] = mapped_column(Text)
  embedding: Mapped[list[float]] = mapped_column(Vector(MODEL_VECTOR_SIZE))
