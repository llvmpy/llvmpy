import unittest
from llvm.core import Module, Type
import llvm.core as lc
from .support import TestCase, tests

class TestArgAttr(TestCase):
    def test_arg_attr(self):
        m = Module.new('oifjda')
        vptr = Type.pointer(Type.float())
        fnty = Type.function(Type.void(), [vptr] * 5)
        func = m.add_function(fnty, 'foo')
        attrs = [lc.ATTR_STRUCT_RET, lc.ATTR_BY_VAL, lc.ATTR_NEST,
                 lc.ATTR_NO_ALIAS, lc.ATTR_NO_CAPTURE]
        for i, attr in enumerate(attrs):
            arg = func.args[i]
            self.assertEqual(i, arg.arg_no)
            arg.add_attribute(attr)
            self.assertTrue(attr in func.args[i])

tests.append(TestArgAttr)

if __name__ == '__main__':
    unittest.main()

