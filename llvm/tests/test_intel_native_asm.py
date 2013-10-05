import sys
import os
import unittest
from llvm.core import Builder, Module, Type
import llvm.core as lc
from .support import TestCase, skip_if_not_intel_cpu, isolated_tests

@skip_if_not_intel_cpu
class TestNativeAsm(TestCase):

    def test_asm(self):
        m = Module.new('module1')

        foo = m.add_function(Type.function(Type.int(),
                                           [Type.int(), Type.int()]),
                             name="foo")
        bldr = Builder.new(foo.append_basic_block('entry'))
        x = bldr.add(foo.args[0], foo.args[1])
        bldr.ret(x)

        att_syntax = m.to_native_assembly()
        os.environ["LLVMPY_OPTIONS"] = "-x86-asm-syntax=intel"
        lc.parse_environment_options(sys.argv[0], "LLVMPY_OPTIONS")
        intel_syntax = m.to_native_assembly()

        self.assertNotEqual(att_syntax, intel_syntax)

isolated_tests.append(__name__)

if __name__ == '__main__':
    unittest.main()
