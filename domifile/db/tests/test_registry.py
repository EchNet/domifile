# db/tests/test_registry.py

import pytest

from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy import Integer

from db.registry import DatabaseRegistry

# --------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------


class Base(DeclarativeBase):
  pass


class Model(Base):
  __tablename__ = "test_registry"
  id = mapped_column(Integer, primary_key=True)


@pytest.fixture
def db_url():
  return "postgresql://localhost:5432/d20gears_test"


# --------------------------------------------------------------
# Tests
# --------------------------------------------------------------


def test_registry_bind_and_session(app, db_url):
  DatabaseRegistry.reset()
  registry = DatabaseRegistry()
  assert registry == DatabaseRegistry.instance()
  registry.bind(Base, db_url)
  registry.seal()
  session = registry.session_for(Model)
  session.close()


def test_registry_health_check(app, db_url):
  DatabaseRegistry.reset()
  registry = DatabaseRegistry()
  assert registry == DatabaseRegistry.instance()
  registry.bind(Base, db_url)
  registry.seal()
  registry.check_health()


def test_registry_seal_prevents_bind(app):
  registry = DatabaseRegistry.instance()
  try:
    registry.bind(Base, "postgresql://ignored")
    assert False
  except RuntimeError:
    pass


def test_get_db_registry_before_init_raises():
  DatabaseRegistry.reset()
  try:
    DatabaseRegistry.instance()
    assert False
  except RuntimeError:
    pass
