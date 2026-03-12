# db/tests/conftest.py
import pytest

from db import DatabaseRegistry


@pytest.fixture(scope="module")
def last_installer():
  from db import Installer
  return Installer


@pytest.fixture(autouse=True)
def reset_db_registry(app):
  try:
    yield
  finally:
    DatabaseRegistry.reset()
