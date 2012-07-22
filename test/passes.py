#!/usr/bin/env python

from llvm.core import *
from llvm.passes import *
from llvm.ee import *

from StringIO import StringIO

import logging, unittest

# A helper class.
class strstream(object):
    def __init__(self, s):
        self.s = s
    def read(self):
        return self.s

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
        pm.add( PASS_FUNCTION_INLINING )

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
        fpm.add( PASS_AGGRESSIVE_DCE )

        # Run the pass on the function 'test1'
        fpm.run( m.get_function_named('test1') )

        # Print the result. Note the change in @test1.
        logging.debug("-"*72)
        logging.debug(m)

        # Make sure test1 is modified
        self.assertNotEqual(str(fn_test1).strip(), original_test1.strip())


if __name__ == '__main__':
    unittest.main()

