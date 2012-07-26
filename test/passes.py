#!/usr/bin/env python

from llvm.core import *
from llvm.passes import *
from llvm.ee import *
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


import logging, unittest

# A helper class.
#class strstream(object):
#    def __init__(self, s):
#        self.s = s
#    def read(self):
#        return self.s

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

class TestPasses(unittest.TestCase):
    def test_passes(self):
        m = Module.from_assembly(StringIO(asm))
        logging.debug("-"*72)
        logging.debug(m)

        fn_test1 = m.get_function_named('test1')
        fn_test2 = m.get_function_named('test2')

        original_test1 = str(fn_test1)
        original_test2 = str(fn_test2)

        # Let's run a module-level inlining pass. First, create a pass manager.
        pm = PassManager.new()

        # Add the target data as the first "pass". This is mandatory.
        pm.add( TargetData.new('') )

        # Add the inlining pass.
        pm.add( PASS_INLINE )

        # Run it!
        pm.run(m)


        # Done with the pass manager.
        del pm

        # Print the result. Note the change in @test2.
        logging.debug("-"*72)
        logging.debug(m)

        # Make sure test2 is inlined
        self.assertNotEqual(str(fn_test2).strip(), original_test2.strip())

        bb_entry = fn_test2.basic_blocks[0]

        self.assertEqual(len(bb_entry.instructions), 1)
        self.assertEqual(bb_entry.instructions[0].opcode_name, 'ret')

        # Let's run a DCE pass on the the function 'test1' now. First create a
        # function pass manager.
        fpm = FunctionPassManager.new(m)

        # Add the target data as first "pass". This is mandatory.
        fpm.add( TargetData.new('') )

        # Add a DCE pass
        fpm.add( PASS_ADCE )

        # Run the pass on the function 'test1'
        fpm.run( m.get_function_named('test1') )

        # Print the result. Note the change in @test1.
        logging.debug("-"*72)
        logging.debug(m)

        # Make sure test1 is modified
        self.assertNotEqual(str(fn_test1).strip(), original_test1.strip())

    def test_passes_with_pmb(self):
        m = Module.from_assembly(StringIO(asm))
        logging.debug("-"*72)
        logging.debug(m)

        fn_test1 = m.get_function_named('test1')
        fn_test2 = m.get_function_named('test2')

        original_test1 = str(fn_test1)
        original_test2 = str(fn_test2)

        # Try out the PassManagerBuilder

        pmb = PassManagerBuilder.new()

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
        self.assertFalse(pmb.disable_simplify_lib_calls)

        # Do function pass
        fpm = FunctionPassManager.new(m)

        pmb.populate(fpm)

        fpm.run(fn_test1)

        # Print the result. Note the change in @test1.
        logging.debug("-"*72)
        logging.debug(m)

        # Make sure test1 has changed
        self.assertNotEqual(str(fn_test1).strip(), original_test1.strip())


        # Do module pass
        pm = PassManager.new()

        pmb.populate(pm)

        pm.run(m)

        # Print the result. Note the change in @test2.
        logging.debug("-"*72)
        logging.debug(m)

        # Make sure test2 has changed
        self.assertNotEqual(str(fn_test2).strip(), original_test2.strip())


    def test_dump_passes(self):
        self.assertTrue(len(PASSES)>0, msg="Cannot have no passes")


if __name__ == '__main__':
    unittest.main()

