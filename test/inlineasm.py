#!/usr/bin/env python

# Import the llvm-py modules.
from llvm import *
from llvm.core import *
from llvm.tests.support import TestCase

import logging
import unittest


class TestInlineAsm(TestCase):
    def test_inline_asm(self):
        mod = Module.new(__name__)
        fnty = Type.function(Type.int(), [Type.int()])
        fn = mod.add_function(fnty, name='test_inline_asm')
        builder = Builder.new(fn.append_basic_block('entry'))

        iaty = Type.function(Type.int(), [Type.int()])
        inlineasm = InlineAsm.get(iaty,  "bswap $0", "=r,r")
        self.assertIn('asm "bswap $0", "=r,r"', str(inlineasm))
        builder.ret(builder.call(inlineasm, [fn.args[0]]))
        print(fn)

if __name__ == '__main__':
    unittest.main()

