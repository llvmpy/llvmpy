import unittest
from llvm.core import (Module, Type, Builder, Constant, inline_function)
from .support import TestCase, tests

class TestInlining(TestCase):
    def test_inline_call(self):
        mod = Module.new(__name__)
        callee = mod.add_function(Type.function(Type.int(), [Type.int()]),
                                  name='bar')

        builder = Builder.new(callee.append_basic_block('entry'))
        builder.ret(builder.add(callee.args[0], callee.args[0]))

        caller = mod.add_function(Type.function(Type.int(), []),
                                  name='foo')

        builder = Builder.new(caller.append_basic_block('entry'))
        callinst = builder.call(callee, [Constant.int(Type.int(), 1234)])
        builder.ret(callinst)

        pre_inlining = str(caller)
        self.assertIn('call', pre_inlining)

        self.assertTrue(inline_function(callinst))

        post_inlining = str(caller)
        self.assertNotIn('call', post_inlining)
        self.assertIn('2468', post_inlining)

tests.append(TestInlining)

if __name__ == '__main__':
    unittest.main()

