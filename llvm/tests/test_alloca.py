import unittest
from llvm.core import Type, Module, Builder, Constant
from .support import TestCase, tests

class TestAlloca(TestCase):
    def test_alloca_alignment(self):
        m = Module.new('')
        f = m.add_function(Type.function(Type.void(), []), "foo")
        b = Builder.new(f.append_basic_block(''))
        inst = b.alloca(Type.int(32))
        inst.alignment = 4
        b.ret_void()
        m.verify()

        self.assertTrue(inst.is_static)
        self.assertFalse(inst.is_array)
        self.assertEqual(inst.alignment, 4)
        self.assertEqual(str(inst.array_size), 'i32 1')

tests.append(TestAlloca)

if __name__ == '__main__':
    unittest.main()

