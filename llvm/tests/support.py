import sys
import unittest
import contextlib
from llvm.tests import tests, isolated_tests # re-expose symbol

IS_PY3K = sys.version_info[0] >= 3
BITS = tuple.__itemsize__ * 8

if sys.version_info[:2] <= (2, 6):
    # create custom TestCase
    class TestCase(unittest.TestCase):
        def assertIn(self, item, container):
            self.assertTrue(item in container)

        def assertNotIn(self, item, container):
            self.assertFalse(item in container)

        def assertLess(self, a, b):
            self.assertTrue(a < b)

        def assertIs(self, a, b):
            self.assertTrue(a is b)

        @contextlib.contextmanager
        def assertRaises(self, exc):
            try:
                yield
            except exc:
                pass
            else:
                raise self.failureException("Did not raise %s" % exc)

else:
    TestCase = unittest.TestCase
