import unittest
from llvm.core import (Module, Type, Builder, Constant)
import llvm.core as lc

from .support import TestCase, tests

class TestConstExpr(TestCase):

    def test_constexpr_opcode(self):
        mod = Module.new('test_constexpr_opcode')
        func = mod.add_function(Type.function(Type.void(), []), name="foo")
        builder = Builder.new(func.append_basic_block('entry'))
        a = builder.inttoptr(Constant.int(Type.int(), 123),
                             Type.pointer(Type.int()))
        self.assertTrue(isinstance(a, lc.ConstantExpr))
        self.assertEqual(a.opcode, lc.OPCODE_INTTOPTR)
        self.assertEqual(a.opcode_name, "inttoptr")

tests.append(TestConstExpr)

if __name__ == '__main__':
    unittest.main()

