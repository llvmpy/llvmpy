import unittest
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from llvm.core import Module
from .support import TestCase, tests

class TestAttr(TestCase):
    def make_module(self):
        test_module = """
            define void @sum(i32*, i32*) {
            entry:
                ret void
            }
        """
        buf = StringIO(test_module)
        return Module.from_assembly(buf)

    def test_align(self):
        m = self.make_module()
        f = m.get_function_named('sum')
        f.args[0].alignment = 16
        self.assert_("align 16" in str(f))
        self.assertEqual(f.args[0].alignment, 16)

tests.append(TestAttr)


if __name__ == '__main__':
    unittest.main()

