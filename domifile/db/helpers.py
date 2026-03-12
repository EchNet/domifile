# domifile/db/helpers.py

from contextlib import contextmanager
from .registry import DatabaseRegistry


@contextmanager
def db_transaction(model_class, *, after_commit=None):
  """
    Context manager that creates a database session scoped to the given model class.

    - Opens a session using get_db_registry().session_for(model_class)
    - Yields the session to the caller for queries/updates
    - Commits if the block exits cleanly
    - Rolls back on any exception and re-raises it
    - Always closes the session afterward

    Intended for short, transaction-scoped database operations.
  """
  session = DatabaseRegistry.instance().session_for(model_class)
  try:
    yield session
    session.commit()
  except Exception:
    session.rollback()
    raise
  finally:
    session.close()
    if after_commit is not None:
      after_commit()
