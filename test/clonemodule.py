#!/usr/bin/env python

# Import the llvm-py modules.
from llvm import *
from llvm.core import *

import logging
import unittest


class TestCloneModule(unittest.TestCase):
    def test_example(self):
        my_module = Module.new('my_module')

        ty_int = Type.int()   # by default 32 bits

        ty_func = Type.function(ty_int, [ty_int, ty_int])

        f_sum = my_module.add_function(ty_func, "sum")

        self.assertEqual(str(f_sum).strip(), 'declare i32 @sum(i32, i32)')

        f_sum.args[0].name = "a"
        f_sum.args[1].name = "b"

        bb = f_sum.append_basic_block("entry")

        builder = Builder.new(bb)

        tmp = builder.add(f_sum.args[0], f_sum.args[1], "tmp")

        self.assertEqual(str(tmp).strip(), '%tmp = add i32 %a, %b')

        builder.ret(tmp)

        cloned = my_module.clone()

        self.assertTrue(id(cloned) != id(my_module))
        self.assertTrue(str(cloned) == str(my_module))
        self.assertTrue(cloned == my_module)



if __name__ == '__main__':
    unittest.main()

