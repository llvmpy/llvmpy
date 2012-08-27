#!/usr/bin/env python

from llvm import *
from llvm.core import *
import sys, os
import unittest

class TestNativeAsm(unittest.TestCase):
    def test_asm(self):
        # create a module
        m = Module.new('module1')

        foo = m.add_function(Type.function(Type.int(), [Type.int(), Type.int()]), name="foo")

        bldr = Builder.new(foo.append_basic_block('entry'))
        x = bldr.add(foo.args[0], foo.args[1])
        bldr.ret(x)

        att_syntax = m.to_native_assembly()
        os.environ["LLVMPY_OPTIONS"] = "-x86-asm-syntax=intel"
        parse_environment_options(sys.argv[0], "LLVMPY_OPTIONS")
        intel_syntax = m.to_native_assembly()

        print(att_syntax)
        print(intel_syntax)
        self.assertNotEqual(att_syntax, intel_syntax)

if __name__ == '__main__':
    unittest.main()
