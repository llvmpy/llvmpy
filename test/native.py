#!/usr/bin/env python

from llvm import *
from llvm.core import *

import unittest, subprocess

class TestNative(unittest.TestCase):

    def _make_module(self):
        m = Module.new('module1')
        m.add_global_variable(Type.int(), 'i')

        fty = Type.function(Type.int(), [])
        f = m.add_function(fty, name='main')

        bldr = Builder.new(f.append_basic_block('entry'))
        bldr.ret(Constant.int(Type.int(), 0xab))

        return m

    def _compile(self, src):
        dst = '/tmp/llvmobj.out'
        s = subprocess.call(['cc', '-o', dst, src])
        if s != 0:
            raise Exception("Cannot compile")

        s = subprocess.call([dst])
        self.assertEqual(s, 0xab)


    def test_assembly(self):
        m = self._make_module()
        output = m.to_native_assembly()

        src = '/tmp/llvmasm.s'
        with open(src, 'wb') as fout:
            fout.write(output)

        self._compile(src)

    def test_object(self):
        m = self._make_module()
        output = m.to_native_object()

        src = '/tmp/llvmobj.o'
        with open(src, 'wb') as fout:
            fout.write(output)

        self._compile(src)

if __name__ == '__main__':
    unittest.main()
