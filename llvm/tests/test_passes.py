import unittest
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import llvm
from llvm.core import Module
import llvm.passes as lp
import llvm.ee as le
from .support import TestCase, tests


class TestPasses(TestCase):
    # Create a module.
    asm = """

define i32 @test() nounwind {
    ret i32 42
}

define i32 @test1() nounwind  {
entry:
        %tmp = alloca i32
        store i32 42, i32* %tmp, align 4
        %tmp1 = load i32* %tmp, align 4
        %tmp2 = call i32 @test()
        %tmp3 = load i32* %tmp, align 4
        %tmp4 = load i32* %tmp, align 4
    ret i32 %tmp1
}

define i32 @test2() nounwind  {
entry:
        %tmp = call i32 @test()
    ret i32 %tmp
}
"""
    def test_passes(self):
        m = Module.from_assembly(StringIO(self.asm))

        fn_test1 = m.get_function_named('test1')
        fn_test2 = m.get_function_named('test2')

        original_test1 = str(fn_test1)
        original_test2 = str(fn_test2)

        # Let's run a module-level inlining pass. First, create a pass manager.
        pm = lp.PassManager.new()

        # Add the target data as the first "pass". This is mandatory.
        pm.add(le.TargetData.new(''))

        # Add the inlining pass.
        pm.add(lp.PASS_INLINE)

        # Run it!
        pm.run(m)

        # Done with the pass manager.
        del pm

        # Make sure test2 is inlined
        self.assertNotEqual(str(fn_test2).strip(), original_test2.strip())

        bb_entry = fn_test2.basic_blocks[0]

        self.assertEqual(len(bb_entry.instructions), 1)
        self.assertEqual(bb_entry.instructions[0].opcode_name, 'ret')

        # Let's run a DCE pass on the the function 'test1' now. First create a
        # function pass manager.
        fpm = lp.FunctionPassManager.new(m)

        # Add the target data as first "pass". This is mandatory.
        fpm.add(le.TargetData.new(''))

        # Add a DCE pass
        fpm.add(lp.PASS_ADCE)

        # Run the pass on the function 'test1'
        fpm.run(m.get_function_named('test1'))

        # Make sure test1 is modified
        self.assertNotEqual(str(fn_test1).strip(), original_test1.strip())

    def test_passes_with_pmb(self):
        m = Module.from_assembly(StringIO(self.asm))

        fn_test1 = m.get_function_named('test1')
        fn_test2 = m.get_function_named('test2')

        original_test1 = str(fn_test1)
        original_test2 = str(fn_test2)

        # Try out the PassManagerBuilder

        pmb = lp.PassManagerBuilder.new()

        self.assertEqual(pmb.opt_level, 2)  # ensure default is level 2
        pmb.opt_level = 3
        self.assertEqual(pmb.opt_level, 3) # make sure it works

        self.assertEqual(pmb.size_level, 0) # ensure default is level 0
        pmb.size_level = 2
        self.assertEqual(pmb.size_level, 2) # make sure it works

        self.assertFalse(pmb.vectorize) # ensure default is False
        pmb.vectorize = True
        self.assertTrue(pmb.vectorize) # make sure it works

        # make sure the default is False
        self.assertFalse(pmb.disable_unit_at_a_time)
        self.assertFalse(pmb.disable_unroll_loops)
        if llvm.version <= (3, 3):
            self.assertFalse(pmb.disable_simplify_lib_calls)

        pmb.disable_unit_at_a_time = True
        self.assertTrue(pmb.disable_unit_at_a_time)

        # Do function pass
        fpm = lp.FunctionPassManager.new(m)
        pmb.populate(fpm)
        fpm.run(fn_test1)

        # Make sure test1 has changed
        self.assertNotEqual(str(fn_test1).strip(), original_test1.strip())

        # Do module pass
        pm = lp.PassManager.new()
        pmb.populate(pm)
        pm.run(m)

        # Make sure test2 has changed
        self.assertNotEqual(str(fn_test2).strip(), original_test2.strip())

    def test_dump_passes(self):
        self.assertTrue(len(lp.PASSES)>0, msg="Cannot have no passes")

tests.append(TestPasses)

if __name__ == '__main__':
    unittest.main()

