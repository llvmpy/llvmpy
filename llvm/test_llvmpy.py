"""
LLVM tests
"""
import os
import sys
import unittest

is_py3k = bool(sys.version_info[0] == 3)

if is_py3k:
    from io import StringIO
else:
    from cStringIO import StringIO


from llvm import __version__
import llvm.core as lc


tests = []

class TestOperands(unittest.TestCase):
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
    def test_operands(self):
        m = lc.Module.from_assembly(StringIO(self.test_module))

        test_func = m.get_function_named("test_func")
        prod = m.get_function_named("prod")

        # test operands
        i1 = test_func.basic_blocks[0].instructions[0]
        i2 = test_func.basic_blocks[0].instructions[1]

        self.assertEqual(i1.operand_count, 3)
        self.assertEqual(i2.operand_count, 2)

        self.assert_(i1.operands[-1] is prod)
        self.assert_(i1.operands[0] is test_func.args[0])
        self.assert_(i1.operands[1] is test_func.args[1])
        self.assert_(i2.operands[0] is i1)
        self.assert_(i2.operands[1] is test_func.args[2])
        self.assertEqual(len(i1.operands), 3)
        self.assertEqual(len(i2.operands), 2)

tests.append(TestOperands)

# ---------------------------------------------------------------------------

def run(verbosity=1):
    print('llvmpy is installed in: ' + os.path.dirname(__file__))
    print('llvmpy version: ' + __version__)
    print(sys.version)

    suite = unittest.TestSuite()
    for cls in tests:
        suite.addTest(unittest.makeSuite(cls))

    runner = unittest.TextTestRunner(verbosity=verbosity)
    return runner.run(suite)


if __name__ == '__main__':
    run()
