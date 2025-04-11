import functools
import inspect

from connectors.drive.DriveFile import DriveFile


def drive_file_operation(*param_names):

  def decorator(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
      sig = inspect.signature(func)
      bound = sig.bind(*args, **kwargs)
      bound.apply_defaults()

      for name, val in bound.arguments.items():
        if (not param_names or name in param_names) and isinstance(val, DriveFile):
          bound.arguments[name] = val.id

      return func(*bound.args, **bound.kwargs)

    return wrapper

  return decorator
