# tests/base.py
import unittest
from app import create_app
from db import db


class FlaskDBTestCase(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    cls.app = create_app(
        "TestConfig", {
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        })
    cls.app_context = cls.app.app_context()
    cls.app_context.push()
    db.create_all()

  @classmethod
  def tearDownClass(cls):
    db.session.remove()
    db.drop_all()
    db.engine.dispose()
    cls.app_context.pop()

  def setUp(self):
    db.session.begin_nested()

  def tearDown(self):
    db.session.rollback()
