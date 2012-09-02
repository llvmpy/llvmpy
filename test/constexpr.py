import unittest
from llvm.core import *

class TestConstExpr(unittest.TestCase):
    def test_constexpr_opcode(self):
        mod = Module.new('test_constexpr_opcode')
        func = mod.add_function(Type.function(Type.void(), []), name="foo")
        builder = Builder.new(func.append_basic_block('entry'))
        a = builder.inttoptr(Constant.int(Type.int(), 123),
                             Type.pointer(Type.int()))
        self.assertTrue(isinstance(a, ConstantExpr))
        self.assertEqual(a.opcode, OPCODE_INTTOPTR)
        self.assertEqual(a.opcode_name, "inttoptr")

if __name__ == '__main__':
    unittest.main()

