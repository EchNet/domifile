# domifile/app/config.py
import os
import sys


class BaseConfig:
  AUTH_URI = "http://localhost:5001"
  CORS_ALLOWED_ORIGINS = []
  GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
  GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
  PORT = 5001
  OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
  OPENAI_API_DEBUG = False
  REDIS_URL = "redis://localhost:6379/0"
  SECRET_KEY = os.getenv("SECRET_KEY") or "default-secret"
  SERVE_STATIC = False
  SESSION_COOKIE_SECURE = True
  SQL_ECHO = os.getenv("SQL_ECHO") == "1"
  TESTING = False
  USE_CELERY = False
  VERBOSE = os.getenv("VERBOSE") == "1"


class DevelopmentConfig(BaseConfig):
  DATABASE_URL = "postgresql+psycopg://localhost:5432/domifile"
  FRONTEND_POST_LOGIN_URL = "http://localhost:5173/"
  DEBUG = True
  ENV = "dev"
  CORS_ALLOWED_ORIGINS = [
      "http://localhost:5173",
      "http://localhost:5001",
  ]
  OPENAI_API_DEBUG = True
  SESSION_COOKIE_SECURE = False


dev = DevelopmentConfig


class TestConfig(BaseConfig):
  DATABASE_URL = "postgresql+psycopg://localhost:5432/domifile_test"
  DEBUG = True
  ENV = "test"
  SERVE_STATIC = True
  SESSION_COOKIE_SECURE = False
  TESTING = True


test = TestConfig


class StagingConfig(BaseConfig):
  AUTH_URI = "https://staging.d20gears.com"
  DEBUG = False
  ENV = "staging"
  FRONTEND_POST_LOGIN_URL = "https://staging.d20gears.com/"
  SERVE_STATIC = True
  USE_CELERY = True


staging = StagingConfig


class ProductionConfig(BaseConfig):
  ENGINE_DATABASE_URL = os.getenv("ENGINE_DATABASE_URL")
  AUTH_URI = "https://domifile.com"
  DEBUG = False
  ENV = "production"
  FRONTEND_POST_LOGIN_URL = "https://domifile.com/"
  SERVE_STATIC = True
  USE_CELERY = True


production = ProductionConfig


def get_app_config():
  this_module = sys.modules[__name__]
  config_key = os.getenv("APP_CONFIG", "DevelopmentConfig")
  return getattr(this_module, config_key)
