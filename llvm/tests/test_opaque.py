import unittest
import llvm
from llvm.core import Type
from .support import TestCase, tests

class TestOpaque(TestCase):

    def test_opaque(self):
        # Create an opaque type
        ts = Type.opaque('mystruct')
        self.assertTrue('type opaque' in str(ts))
        self.assertTrue(ts.is_opaque)
        self.assertTrue(ts.is_identified)
        self.assertFalse(ts.is_literal)
        #print(ts)

        # Create a recursive type
        ts.set_body([Type.int(), Type.pointer(ts)])

        self.assertEqual(ts.elements[0], Type.int())
        self.assertEqual(ts.elements[1], Type.pointer(ts))
        self.assertEqual(ts.elements[1].pointee, ts)
        self.assertFalse(ts.is_opaque) # is not longer a opaque type
        #print(ts)

        with self.assertRaises(llvm.LLVMException):
            # Cannot redefine
            ts.set_body([])

    def test_opaque_with_no_name(self):
        with self.assertRaises(llvm.LLVMException):
            Type.opaque('')

tests.append(TestOpaque)

if __name__ == '__main__':
    unittest.main()

