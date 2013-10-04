import unittest
from llvm.core import Module, Type, Builder, Constant
from llvm.ee import EngineBuilder
import llvm.ee as le
import llvmpy

from .support import TestCase, tests

class TestEngineBuilder(TestCase):

    def make_test_module(self):
        module = Module.new("testmodule")
        fnty = Type.function(Type.int(), [])
        function = module.add_function(fnty, 'foo')
        bb_entry = function.append_basic_block('entry')
        builder = Builder.new(bb_entry)
        builder.ret(Constant.int(Type.int(), 0xcafe))
        module.verify()
        return module

    def run_foo(self, ee, module):
        function = module.get_function_named('foo')
        retval = ee.run_function(function, [])
        self.assertEqual(retval.as_int(), 0xcafe)


    def test_enginebuilder_basic(self):
        module = self.make_test_module()
        self.assertTrue(llvmpy.capsule.has_ownership(module._ptr._ptr))
        ee = EngineBuilder.new(module).create()
        self.assertFalse(llvmpy.capsule.has_ownership(module._ptr._ptr))
        self.run_foo(ee, module)


    def test_enginebuilder_with_tm(self):
        tm = le.TargetMachine.new()
        module = self.make_test_module()
        self.assertTrue(llvmpy.capsule.has_ownership(module._ptr._ptr))
        ee = EngineBuilder.new(module).create(tm)
        self.assertFalse(llvmpy.capsule.has_ownership(module._ptr._ptr))
        self.run_foo(ee, module)

    def test_enginebuilder_force_jit(self):
        module = self.make_test_module()
        ee = EngineBuilder.new(module).force_jit().create()

        self.run_foo(ee, module)
#
#    def test_enginebuilder_force_interpreter(self):
#        module = self.make_test_module()
#        ee = EngineBuilder.new(module).force_interpreter().create()
#
#        self.run_foo(ee, module)

    def test_enginebuilder_opt(self):
        module = self.make_test_module()
        ee = EngineBuilder.new(module).opt(3).create()

        self.run_foo(ee, module)

tests.append(TestEngineBuilder)

if __name__ == '__main__':
    unittest.main()

