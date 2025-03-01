import pytest
from main import app
from db import db


@pytest.fixture
def client():
  app.config['TESTING'] = True
  app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # In-memory DB for tests

  with app.test_client() as client:
    with app.app_context():
      db.create_all()  # Create tables
    yield client
    with app.app_context():
      db.session.remove()
      db.drop_all()  # Drop all tables after the test
