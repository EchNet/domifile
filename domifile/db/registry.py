# domifile/db/registry.py

from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

from domifile.utils.registry import SingletonRegistry


class DatabaseRegistry(SingletonRegistry):
  """
    Maps a DeclarativeBase -> SQLAlchemy engine and sessionmaker.
    Allows each model base to live in any DB.
  """

  def __init__(self, config=None):
    super().__init__()
    self._echo = config.SQL_ECHO if config else False

  def bind(self, base, url, *, echo=False):
    engine = create_engine(url, echo=self._echo, future=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False)

    base.metadata.bind = engine

    self.register(base, (engine, SessionLocal))

  def create_all(self):
    for base, (engine, _) in self.items():
      base.metadata.create_all(engine)

  def drop_all(self):
    for base, (engine, _) in self.items():
      base.metadata.drop_all(engine)

  def session_for(self, model):
    base = model.__bases__[0]
    _, SessionLocal = self.get(base, required=True)
    return SessionLocal()

  def check_health(self):
    count = 0
    for engine, _ in self.values():
      with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
      count += 1
    if count == 0:
      raise ValueError("No databases are registered")
