import unittest
from llvm.core import Type
import llvm.core as lc
import llvm.ee as le

from .support import TestCase, tests

class TestExecutionEngine(TestCase):
    def test_get_pointer_to_global(self):
        module = lc.Module.new(str(self))
        gvar = module.add_global_variable(Type.int(), 'hello')
        X = 1234
        gvar.initializer = lc.Constant.int(Type.int(), X)

        ee = le.ExecutionEngine.new(module)
        ptr = ee.get_pointer_to_global(gvar)
        from ctypes import c_void_p, cast, c_int, POINTER
        casted = cast(c_void_p(ptr), POINTER(c_int))
        self.assertEqual(X, casted[0])

    def test_add_global_mapping(self):
        module = lc.Module.new(str(self))
        gvar = module.add_global_variable(Type.int(), 'hello')

        fnty = lc.Type.function(Type.int(), [])
        foo = module.add_function(fnty, name='foo')
        bldr = lc.Builder.new(foo.append_basic_block('entry'))
        bldr.ret(bldr.load(gvar))

        ee = le.ExecutionEngine.new(module)
        from ctypes import c_int, addressof, CFUNCTYPE
        value = 0xABCD
        value_ctype = c_int(value)
        value_pointer = addressof(value_ctype)

        ee.add_global_mapping(gvar, value_pointer)

        foo_addr = ee.get_pointer_to_function(foo)
        prototype = CFUNCTYPE(c_int)
        foo_callable = prototype(foo_addr)
        self.assertEqual(foo_callable(), value)

tests.append(TestExecutionEngine)

if __name__ == '__main__':
    unittest.main()

