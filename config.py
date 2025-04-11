# config.py

import os


class BaseConfig:
  GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
  GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
  SECRET_KEY = os.getenv("SECRET_KEY") or "default-secret"
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  TESTING = False
  USE_CELERY = False
  VERBOSE = os.getenv("VERBOSE") == "1"


class DevelopmentConfig(BaseConfig):
  DEBUG = True
  ENV = "dev"
  SQLALCHEMY_DATABASE_URI = "sqlite:///dev.sqlite3"


class TestConfig(BaseConfig):
  DEBUG = True
  ENV = "test"
  SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
  TESTING = True


class StagingConfig(BaseConfig):
  DEBUG = False
  ENV = "staging"
  SQLALCHEMY_DATABASE_URI = "sqlite:///db.sqlite3"
  USE_CELERY = True


class ProductionConfig(BaseConfig):
  DEBUG = False
  ENV = "production"
  SQLALCHEMY_DATABASE_URI = "sqlite:///db.sqlite3"
  USE_CELERY = True
