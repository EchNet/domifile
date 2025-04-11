import os


class ResourceProvider:

  def __init__(self, **kwargs):
    self._cache_ = {**kwargs}

  def __getattr__(self, name):
    # Avoid infinite recursion by using object.__getattribute__
    cache = object.__getattribute__(self, "_cache_")
    if name in cache:
      return cache[name]

    getter_name = f"get_{name}"
    try:
      getter = object.__getattribute__(self, getter_name)
      val = getter()
      cache[name] = val
      return val
    except AttributeError:
      pass

    raise AttributeError(f"No such property: {name}")
