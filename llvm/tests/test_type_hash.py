import unittest
from llvm.core import Type
from .support import TestCase, tests

class TestTypeHash(TestCase):
    def test_scalar_type(self):
        i32a = Type.int(32)
        i32b = Type.int(32)
        i64a = Type.int(64)
        i64b = Type.int(64)
        ts = set([i32a, i32b, i64a, i64b])
        self.assertTrue(len(ts))
        self.assertTrue(i32a in ts)
        self.assertTrue(i64b in ts)

    def test_struct_type(self):
        ta = Type.struct([Type.int(32), Type.float()])
        tb = Type.struct([Type.int(32), Type.float()])
        tc = Type.struct([Type.int(32), Type.int(32), Type.float()])
        ts = set([ta, tb, tc])
        self.assertTrue(len(ts) == 2)
        self.assertTrue(ta in ts)
        self.assertTrue(tb in ts)
        self.assertTrue(tc in ts)

tests.append(TestTypeHash)

if __name__ == '__main__':
    unittest.main()

