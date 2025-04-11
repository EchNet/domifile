import unittest
from unittest.mock import Mock

from actions.action import Action


class TestAction(Action):

  @property
  def name(self):
    return "Say Hello"

  def execute_action(self):
    return f"I said hello to {self.args[0]} in {self.context}"


class TestGreeterBehavior(unittest.TestCase):

  def test_name(self):
    a = TestAction(Mock())
    self.assertEqual(a.name, "Say Hello")

  def test_act(self):
    mock_context = Mock()
    mock_context.__str__ = lambda self=mock_context: "Context"
    mock_logger = Mock()
    mock_context.logger = mock_logger
    a = TestAction(mock_context, "Arnie")
    a.act()
    self.assertEqual(mock_logger.info.call_count, 1)
    mock_logger.info.assert_called_with("I said hello to Arnie in Context")


if __name__ == "__main__":
  unittest.main()
