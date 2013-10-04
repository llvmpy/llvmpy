import unittest
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from llvm.core import Module
from .support import TestCase, tests

class TestOperands(TestCase):
    # implement a test function
    test_module = """
define i32 @prod(i32, i32) {
entry:
        %2 = mul i32 %0, %1
        ret i32 %2
}

define i32 @test_func(i32, i32, i32) {
entry:
        %tmp1 = call i32 @prod(i32 %0, i32 %1)
        %tmp2 = add i32 %tmp1, %2
        %tmp3 = add i32 %tmp2, 1
        %tmp4 = add i32 %tmp3, -1
        %tmp5 = add i64 -81985529216486895, 12297829382473034410
        ret i32 %tmp4
}
"""
    def test_operands(self):
        m = Module.from_assembly(StringIO(self.test_module))

        test_func = m.get_function_named("test_func")
        prod = m.get_function_named("prod")

        # test operands
        i1 = test_func.basic_blocks[0].instructions[0]
        i2 = test_func.basic_blocks[0].instructions[1]
        i3 = test_func.basic_blocks[0].instructions[2]
        i4 = test_func.basic_blocks[0].instructions[3]
        i5 = test_func.basic_blocks[0].instructions[4]

        self.assertEqual(i1.operand_count, 3)
        self.assertEqual(i2.operand_count, 2)

        self.assertEqual(i3.operands[1].z_ext_value, 1)
        self.assertEqual(i3.operands[1].s_ext_value, 1)
        self.assertEqual(i4.operands[1].z_ext_value, 0xffffffff)
        self.assertEqual(i4.operands[1].s_ext_value, -1)
        self.assertEqual(i5.operands[0].s_ext_value, -81985529216486895)
        self.assertEqual(i5.operands[1].z_ext_value, 12297829382473034410)

        self.assert_(i1.operands[-1] is prod)
        self.assert_(i1.operands[0] is test_func.args[0])
        self.assert_(i1.operands[1] is test_func.args[1])
        self.assert_(i2.operands[0] is i1)
        self.assert_(i2.operands[1] is test_func.args[2])
        self.assertEqual(len(i1.operands), 3)
        self.assertEqual(len(i2.operands), 2)

        self.assert_(i1.called_function is prod)

tests.append(TestOperands)

if __name__ == '__main__':
    unittest.main()

