# domifile/models.py
from datetime import datetime
from sqlalchemy import Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from pgvector.sqlalchemy import Vector


class Base(DeclarativeBase):
  """Declarative base for Resource."""
  pass


class Document(Base):
  __tablename__ = "documents"

  id: Mapped[int] = mapped_column(Integer, primary_key=True)

  drive_file_id: Mapped[str] = mapped_column(
      String,
      index=True,
      unique=True,
      nullable=False,
  )
  filename: Mapped[str] = mapped_column(String)
  mime_type: Mapped[str] = mapped_column(String)

  drive_modified_time: Mapped[datetime] = mapped_column(DateTime)
  ingested_at: Mapped[datetime] = mapped_column(DateTime)

  text: Mapped[str] = mapped_column(Text)


MODEL_VECTOR_SIZE = 1536  # OpenAI dependency: text-embedding-3-small


class Chunk(Base):
  __tablename__ = "chunks"

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"))
  text: Mapped[str] = mapped_column(Text)
  embedding: Mapped[list[float]] = mapped_column(Vector(MODEL_VECTOR_SIZE))
