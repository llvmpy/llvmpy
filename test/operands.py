#!/usr/bin/env python

# Tests accessing of instruction operands.
import sys
import logging
import unittest

from llvm.core import *
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

m = None

#===----------------------------------------------------------------------===

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
        ret i32 %tmp3
}
"""

class TestOperands(unittest.TestCase):

    def test_operands(self):
        m = Module.from_assembly(StringIO(test_module))
        logging.debug("-"*60)
        logging.debug(m)
        logging.debug("-"*60)

        test_func = m.get_function_named("test_func")
        prod      = m.get_function_named("prod")

        #===-----------------------------------------------------------===
        # test operands


        i1 = test_func.basic_blocks[0].instructions[0]
        i2 = test_func.basic_blocks[0].instructions[1]
        logging.debug("Testing User.operand_count ..")

        self.assertEqual(i1.operand_count, 3)
        self.assertEqual(i2.operand_count, 2)

        logging.debug("Testing User.operands ..")

        self.assert_(i1.operands[-1] is prod)
        self.assert_(i1.operands[0] is test_func.args[0])
        self.assert_(i1.operands[1] is test_func.args[1])
        self.assert_(i2.operands[0] is i1)
        self.assert_(i2.operands[1] is test_func.args[2])
        self.assertEqual(len(i1.operands), 3)
        self.assertEqual(len(i2.operands), 2)

        #===-----------------------------------------------------------===
        # show test_function

        logging.debug("Examining test_function `test_test_func':")

        idx = 1
        for inst in test_func.basic_blocks[0].instructions:
            logging.debug("Instruction #%d:", idx)
            logging.debug("  operand_count = %d", inst.operand_count)
            logging.debug("  operands:")
            oidx = 1
            for op in inst.operands:
                logging.debug("    %d: %s", oidx, repr(op))
                oidx += 1
            idx += 1

if __name__ == '__main__':
    unittest.main()
