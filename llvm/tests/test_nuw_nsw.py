import unittest
from llvm.core import Module, Type, Builder
from .support import TestCase, tests

class TestNUWNSW(TestCase):
    def make_module(self):
        mod = Module.new('asdfa')
        fnty = Type.function(Type.void(), [Type.int()] * 2)
        func = mod.add_function(fnty, 'foo')
        bldr = Builder.new(func.append_basic_block(''))
        return mod, func, bldr

    def has_nsw(self, inst, op):
        self.assertTrue(('%s nsw' % op) in str(inst), "NSW flag does not work")

    def has_nuw(self, inst, op):
        self.assertTrue(('%s nuw' % op) in str(inst), "NUW flag does not work")

    def _test_template(self, opf, opname):
        mod, func, bldr = self.make_module()
        a, b = func.args
        self.has_nsw(opf(bldr, a, b, nsw=True), opname)
        self.has_nuw(opf(bldr, a, b, nuw=True), opname)

    def test_add_nuw_nsw(self):
        self._test_template(Builder.add, 'add')

    def test_sub_nuw_nsw(self):
        self._test_template(Builder.sub, 'sub')

    def test_mul_nuw_nsw(self):
        self._test_template(Builder.mul, 'mul')

    def test_shl_nuw_nsw(self):
        self._test_template(Builder.shl, 'shl')

    def test_neg_nuw_nsw(self):
        mod, func, bldr = self.make_module()
        a, b = func.args
        self.has_nsw(bldr.neg(a, nsw=True), 'sub')
        self.has_nuw(bldr.neg(a, nuw=True), 'sub')


tests.append(TestNUWNSW)

if __name__ == '__main__':
    unittest.main()

