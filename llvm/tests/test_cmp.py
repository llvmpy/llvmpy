import unittest
from llvm.core import (Module, Type, Builder, Constant)
import llvm.core as lc
from .support import TestCase, tests

class TestCmp(TestCase):
    def test_arg_attr(self):
        m = Module.new('oifjda')
        fnty = Type.function(Type.void(), [Type.int()])
        func = m.add_function(fnty, 'foo')
        bb = func.append_basic_block('')
        bldr = Builder.new(bb)

        cmpinst = bldr.icmp(lc.ICMP_ULE, func.args[0],
                            Constant.int(Type.int(), 123))
        self.assertTrue(repr(cmpinst.predicate).startswith('ICMP_ULE'))
        self.assertEqual(cmpinst.predicate, lc.ICMP_ULE)
        bldr.ret_void()

        func.verify()

tests.append(TestCmp)

if __name__ == '__main__':
    unittest.main()

