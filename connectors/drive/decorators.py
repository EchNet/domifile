import functools
import inspect

from connectors.drive.DriveFile import DriveFile


def drive_file_id_operation(*param_names):
  """
    Decorator that replaces all DriveFiles found in the argument list with
    their IDs.

      @drive_file_id_operation
      def func1(file1, file2):
        pass

    Optionally, the parameters to coerce to file IDs may be specified.

      @drive_file_id_operation("file2")
      def func2(file1, file2):
        pass
  """

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
