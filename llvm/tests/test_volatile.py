import unittest
from llvm.core import Module, Type, Builder
from .support import TestCase, tests

class TestVolatile(TestCase):

    def test_volatile(self):
        mod = Module.new('mod')
        functype = Type.function(Type.void(), [])
        func = mod.add_function(functype, name='foo')
        bb = func.append_basic_block('entry')
        bldr = Builder.new(bb)
        ptr = bldr.alloca(Type.int())

        # test load inst
        val = bldr.load(ptr)
        self.assertFalse(val.is_volatile, "default must be non-volatile")
        val.set_volatile(True)
        self.assertTrue(val.is_volatile, "fail to set volatile")
        val.set_volatile(False)
        self.assertFalse(val.is_volatile, "fail to unset volatile")

        # test store inst
        store_inst = bldr.store(val, ptr)
        self.assertFalse(store_inst.is_volatile, "default must be non-volatile")
        store_inst.set_volatile(True)
        self.assertTrue(store_inst.is_volatile, "fail to set volatile")
        store_inst.set_volatile(False)
        self.assertFalse(store_inst.is_volatile, "fail to unset volatile")

    def test_volatile_another(self):
        mod = Module.new('mod')
        functype = Type.function(Type.void(), [])
        func = mod.add_function(functype, name='foo')
        bb = func.append_basic_block('entry')
        bldr = Builder.new(bb)
        ptr = bldr.alloca(Type.int())

        # test load inst
        val = bldr.load(ptr, volatile=True)
        self.assertTrue(val.is_volatile, "volatile kwarg does not work")
        val.set_volatile(False)
        self.assertFalse(val.is_volatile, "fail to unset volatile")
        val.set_volatile(True)
        self.assertTrue(val.is_volatile, "fail to set volatile")

        # test store inst
        store_inst = bldr.store(val, ptr, volatile=True)
        self.assertTrue(store_inst.is_volatile, "volatile kwarg does not work")
        store_inst.set_volatile(False)
        self.assertFalse(store_inst.is_volatile, "fail to unset volatile")
        store_inst.set_volatile(True)
        self.assertTrue(store_inst.is_volatile, "fail to set volatile")

tests.append(TestVolatile)

if __name__ == '__main__':
    unittest.main()

