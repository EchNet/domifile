# utils/registry.py
import logging

logger = logging.getLogger("registries-debug")


class BaseRegistry:
  """
    A common Registry pattern.  Usage pattern is:
      - Instantiate to create empty registry.
      - Register values.
      - Seal the registry to prevent further changes.
      - Use the registry.
  """

  def __init__(self):
    """ Subclass initializers must call this initializer. """
    self._items = {}
    self._sealed = False
    self._closed = False  # For unit tests

  def register(self, key, value):
    if self._closed:
      raise RuntimeError(f"{self.__class__.__name__} is closed")
    if self._sealed:
      raise RuntimeError(f"{self.__class__.__name__} is sealed")

    if key in self._items:
      raise RuntimeError(f"Duplicate key: {key}")

    self._items[key] = value

  def seal(self):
    self._sealed = True

  def close(self):
    self._closed = True

  def get(self, key, *, required=False):
    if self._closed:
      raise RuntimeError(f"{self.__class__.__name__} is closed")
    if not self._sealed:
      raise RuntimeError(f"{self.__class__.__name__} is not sealed")
    if not key in self._items:
      if required:
        raise RuntimeError(f"{key} not found in {self.__class__.__name__}")
      return None
    return self._items[key]

  def items(self):
    if self._closed:
      raise RuntimeError(f"{self.__class__.__name__} is closed")
    if not self._sealed:
      raise RuntimeError(f"{self.__class__.__name__} is not sealed")
    return self._items.items()

  def values(self):
    if self._closed:
      raise RuntimeError(f"{self.__class__.__name__} is closed")
    if not self._sealed:
      raise RuntimeError(f"{self.__class__.__name__} is not sealed")
    return self._items.values()


class SingletonRegistry(BaseRegistry):
  """
    A common Registry pattern.  Registry is a singleton.  Usage pattern is:
      - Call constructor to create singleton instance.
      - Register values with instance.
      - Seal the instance.
      - Access instance through class.
  """
  _instance = None

  def __init__(self):
    """ Subclass initializers must call this initializer. """
    logger.debug(f"Initializing {self.__class__.__name__}")
    super().__init__()
    self.set_instance(self)

  # ---- Singleton access ----

  @classmethod
  def set_instance(cls, instance):
    if cls._instance is not None:
      raise RuntimeError(f"{cls.__name__} already initialized")
    cls._instance = instance

  @classmethod
  def instance(cls):
    if cls._instance is None:
      raise RuntimeError(f"{cls.__name__} not initialized")
    return cls._instance

  # ---- Test-only ----

  @classmethod
  def reset(cls):
    logger.debug(f"Resetting {cls.__name__}")

    if not cls._allow_reset():
      raise RuntimeError("reset() allowed only in tests")

    if cls._instance:
      cls._instance.close()

    cls._instance = None

  @staticmethod
  def _allow_reset():
    import sys
    return "pytest" in sys.modules
