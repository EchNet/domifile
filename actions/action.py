from abc import ABC, abstractmethod
from errors import AuthorizationError, ApplicationError


class Action(ABC):

  def __init__(self, context, *args, **kwargs):
    self.context = context
    self.args = args
    self.kwargs = kwargs

  @abstractmethod
  def execute_action(self):
    pass

  @property
  @abstractmethod
  def name(self):
    pass

  def act(self):
    try:
      summary = self.execute_action()
      self.log_action_summary(summary)
    except AuthorizationError as e:
      self.log_authorization_error(e)
    except ApplicationError as e:
      self.log_application_error(e)
    except Exception as e:
      self.log_unexpected_error(e)

  def log_action_summary(self, summary):
    # TODO:
    self.context.logger.info(summary)

  def log_authorization_error(self, e):
    # TODO
    self.context.logger.error(e)

  def log_application_error(self, e):
    # TODO
    self.context.logger.error(e)

  def log_unexpected_error(self, e):
    # TODO
    self.context.logger.error(e)
