import unittest
from llvm.core import (Module, Type, Builder)
from .support import TestCase, tests

class TestExact(TestCase):
    def make_module(self):
        mod = Module.new('asdfa')
        fnty = Type.function(Type.void(), [Type.int()] * 2)
        func = mod.add_function(fnty, 'foo')
        bldr = Builder.new(func.append_basic_block(''))
        return mod, func, bldr

    def has_exact(self, inst, op):
        self.assertTrue(('%s exact' % op) in str(inst), "exact flag does not work")

    def _test_template(self, opf, opname):
        mod, func, bldr = self.make_module()
        a, b = func.args
        self.has_exact(opf(bldr, a, b, exact=True), opname)

    def test_udiv_exact(self):
        self._test_template(Builder.udiv, 'udiv')

    def test_sdiv_exact(self):
        self._test_template(Builder.sdiv, 'sdiv')

    def test_lshr_exact(self):
        self._test_template(Builder.lshr, 'lshr')

    def test_ashr_exact(self):
        self._test_template(Builder.ashr, 'ashr')

tests.append(TestExact)

if __name__ == '__main__':
    unittest.main()

