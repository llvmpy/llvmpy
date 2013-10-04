import unittest
from llvm.core import (Module, Type, Builder, Constant)

from .support import TestCase, tests

class TestSwitch(TestCase):
    def test_arg_attr(self):
        m = Module.new('oifjda')
        fnty = Type.function(Type.void(), [Type.int()])
        func = m.add_function(fnty, 'foo')
        bb = func.append_basic_block('')
        bbdef = func.append_basic_block('')
        bbsw1 = func.append_basic_block('')
        bbsw2 = func.append_basic_block('')
        bldr = Builder.new(bb)

        swt = bldr.switch(func.args[0], bbdef, n=2)
        swt.add_case(Constant.int(Type.int(), 0), bbsw1)
        swt.add_case(Constant.int(Type.int(), 1), bbsw2)

        bldr.position_at_end(bbsw1)
        bldr.ret_void()

        bldr.position_at_end(bbsw2)
        bldr.ret_void()

        bldr.position_at_end(bbdef)
        bldr.ret_void()

        func.verify()

tests.append(TestSwitch)

if __name__ == '__main__':
    unittest.main()

