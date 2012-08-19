#!/usr/bin/env python

# Import the llvm-py modules.
from llvm import *
from llvm.core import *
from llvm.ee import *          # new import: ee = Execution Engine

import logging
import unittest


class TestExampleJIT(unittest.TestCase):
    def test_example_jit(self):
        # Create a module, as in the previous example.
        my_module = Module.new('my_module')
        ty_int = Type.int()   # by default 32 bits
        ty_func = Type.function(ty_int, [ty_int, ty_int])
        f_sum = my_module.add_function(ty_func, "sum")
        f_sum.args[0].name = "a"
        f_sum.args[1].name = "b"
        bb = f_sum.append_basic_block("entry")
        builder = Builder.new(bb)
        tmp = builder.add(f_sum.args[0], f_sum.args[1], "tmp")
        builder.ret(tmp)

        # Create an execution engine object. This will create a JIT compiler
        # on platforms that support it, or an interpreter otherwise.
        ee = ExecutionEngine.new(my_module)

        # The arguments needs to be passed as "GenericValue" objects.
        arg1_value = 100
        arg2_value = 42

        arg1 = GenericValue.int(ty_int, arg1_value)
        arg2 = GenericValue.int(ty_int, arg2_value)

        # Now let's compile and run!
        retval = ee.run_function(f_sum, [arg1, arg2])

        # The return value is also GenericValue. Let's print it.
        logging.debug("returned %d", retval.as_int())

        self.assertEqual(retval.as_int(), (arg1_value + arg2_value))


if __name__ == '__main__':
    unittest.main()

