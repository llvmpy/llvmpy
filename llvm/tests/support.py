from __future__ import print_function, division
import sys
import platform
import unittest
import contextlib
import types

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from llvm.tests import tests, isolated_tests # re-expose symbol

IS_PY3K = sys.version_info[0] >= 3
BITS = tuple.__itemsize__ * 8
OS = sys.platform
MACHINE = platform.machine()
INTEL_CPUS = 'i386', 'x86_64'

if sys.version_info[:2] <= (2, 6):
    # create custom TestCase
    class _TestCase(unittest.TestCase):
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
    _TestCase = unittest.TestCase


class TestCase(_TestCase):
    def assertClose(self, got, expect):
        rel = abs(got - expect) / expect
        self.assertTrue(rel < 1e-6, 'relative error = %f' % rel)

#-------------------------------------------------------------------------------
# Tests decorators

skip_if = unittest.skipIf

skip_if_not_64bits = skip_if(BITS != 64, 'skipped not 64-bit')

skip_if_not_32bits = skip_if(BITS != 32, 'skipped not 32-bits')

skip_if_win32 = skip_if(OS.startswith('win32'), 'skipped win32')

skip_if_not_win32 = skip_if(not OS.startswith('win32'),
                            'skipped not win32')
skip_if_not_intel_cpu = skip_if(MACHINE not in INTEL_CPUS,
                                'skipped not Intel CPU')


