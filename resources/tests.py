import json
import unittest

from resources import ResourceProvider


class RpMixin1(ResourceProvider):

  def get_simple_prop(self):
    return "simple"

  def get_derived_prop(self):
    return f"{self.simple_prop} 1"


class RpMixin2(ResourceProvider):

  def get_derived_prop(self):
    return "derived"


class RpMixin3(ResourceProvider):
  pass


class TestResourceProvider(RpMixin1, RpMixin2, RpMixin3):
  pass


class ResourceProviderTestCase(unittest.TestCase):

  def test_miss(self):
    rp = TestResourceProvider()
    with self.assertRaises(AttributeError):
      rp.no_such_prop

  def test_simple_and_derived(self):
    rp = TestResourceProvider()
    self.assertEqual(rp.simple_prop, "simple")
    self.assertEqual(rp.derived_prop, "simple 1")


if __name__ == "__main__":
  unittest.main()
