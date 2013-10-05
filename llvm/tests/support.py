from __future__ import print_function, division
import sys
import platform
import unittest
import contextlib
import types
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

def _skipped(name, msg):
    def _test(self):
        if hasattr(unittest, 'SkipTest'):
            raise unittest.SkipTest(msg)
        else:
            print('skipped %s' % name, msg)
    return _test

def skip_if(cond, msg=''):
    def skipper(test):
        if not isinstance(test, types.FunctionType):
            repl = None
        else:
            repl = _skipped(test, msg)
        return repl if cond else test
    return skipper

skip_if_not_64bits = skip_if(BITS != 64, msg='skipped not 64-bit')

skip_if_not_32bits = skip_if(BITS != 32, msg='skipped not 32-bits')

skip_if_win32 = skip_if(OS.startswith('win32'), msg='skipped win32')

skip_if_not_win32 = skip_if(not OS.startswith('win32'),
                            msg='skipped not win32')
skip_if_not_intel_cpu = skip_if(MACHINE not in INTEL_CPUS,
                                msg='skipped not Intel CPU')


