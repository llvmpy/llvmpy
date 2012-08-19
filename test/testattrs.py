#!/usr/bin/env python

from llvm.core import *
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


import unittest

def make_module():
    test_module = """
    define i32 @sum(i32, i32) {
    entry:
            %2 = add i32 %0, %1
            ret i32 %2
    }
    """
    return Module.from_assembly(StringIO(test_module))

class TestAttr(unittest.TestCase):
    def test_align(self):
        m = make_module()
        f = m.get_function_named('sum')
        f.args[0].alignment = 16
        self.assertIn("align 16", str(f))
        self.assertEqual(f.args[0].alignment, 16)

if __name__ == '__main__':
    unittest.main()
