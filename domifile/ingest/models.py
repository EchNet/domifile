# domifile/ingest/models.py

from sqlalchemy import Integer, String, Text, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
  """Declarative base for Resource."""
  pass


class Document(Base):
  __tablename__ = "documents"

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  drive_file_id: Mapped[str] = mapped_column(String)
  filename: Mapped[str] = mapped_column(String)
  text: Mapped[str] = mapped_column(Text)


class Chunk(Base):
  __tablename__ = "chunks"

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"))
  text: Mapped[str] = mapped_column(Text)
