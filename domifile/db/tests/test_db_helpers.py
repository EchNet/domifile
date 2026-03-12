# tests/test_db_helpers.py

import pytest
from db.helpers import db_transaction


class DummySession:

  def __init__(self):
    self.committed = False
    self.rolled_back = False
    self.closed = False

  def commit(self):
    self.committed = True

  def rollback(self):
    self.rolled_back = True

  def close(self):
    self.closed = True


class DummyRegistry:

  def __init__(self, session):
    self._session = session

  def session_for(self, model_class):
    return self._session


@pytest.fixture
def patch_registry(monkeypatch):

  def _patch(session):
    dummy = DummyRegistry(session)
    monkeypatch.setattr("db.helpers.DatabaseRegistry.instance", lambda: dummy)

  return _patch


def test_commit_on_success(patch_registry):
  session = DummySession()
  patch_registry(session)

  with db_transaction(object):
    pass

  assert session.committed
  assert not session.rolled_back
  assert session.closed


def test_rollback_on_exception(patch_registry):
  session = DummySession()
  patch_registry(session)

  with pytest.raises(ValueError):
    with db_transaction(object):
      raise ValueError("boom")

  assert not session.committed
  assert session.rolled_back
  assert session.closed


def test_after_commit_called(patch_registry):
  session = DummySession()
  patch_registry(session)

  called = {"flag": False}

  def after():
    called["flag"] = True

  with db_transaction(object, after_commit=after):
    pass

  assert called["flag"]
