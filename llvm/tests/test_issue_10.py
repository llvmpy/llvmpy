import unittest
from llvm.core import (Module, Type, Builder)
from .support import TestCase, tests

class TestIssue10(TestCase):
    def test_issue10(self):
        m = Module.new('a')
        ti = Type.int()
        tf = Type.function(ti, [ti, ti])

        f = m.add_function(tf, "func1")

        bb = f.append_basic_block('entry')

        b = Builder.new(bb)

        # There are no instructions in bb. Positioning of the
        # builder at beginning (or end) should succeed (trivially).
        b.position_at_end(bb)
        b.position_at_beginning(bb)

tests.append(TestIssue10)

if __name__ == '__main__':
    unittest.main()

