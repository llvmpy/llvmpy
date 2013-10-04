import unittest
from llvm.core import Type
from .support import TestCase, tests

class TestStruct(TestCase):
    def test_struct_identical(self):
        ta = Type.struct([Type.int(32), Type.float()], name='ta')
        tb = Type.struct([Type.int(32), Type.float()])
        self.assertTrue(ta.is_layout_identical(tb))

tests.append(TestStruct)

if __name__ == '__main__':
    unittest.main()

