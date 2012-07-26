#!/usr/bin/env python

from llvm import *
from llvm.core import *

import unittest

class TestAsm(unittest.TestCase):
    def test_asm(self):
        # create a module
        m = Module.new('module1')
        m.add_global_variable(Type.int(), 'i')

        # write it's assembly representation to a file
        asm = str(m)

        with open("/tmp/testasm.ll", "w") as fout:
            fout.write(asm)

        # read it back into a module
        with open("/tmp/testasm.ll") as fin:
            m2 = Module.from_assembly(fin)
            # The default `m.id` is '<string>'.
            m2.id = m.id # Copy the name from `m`

        self.assertEqual(str(m2).strip(), asm.strip())


    def test_bitcode(self):
        # create a module
        m = Module.new('module1')
        m.add_global_variable(Type.int(), 'i')

        # write it's assembly representation to a file
        asm = str(m)

        with open("/tmp/testasm.bc", "wb") as fout:
            m.to_bitcode(fout)

        # read it back into a module
        with open("/tmp/testasm.bc", "rb") as fin:
            m2 = Module.from_bitcode(fin)
            # The default `m.id` is '<string>'.
            m2.id = m.id # Copy the name from `m`

        self.assertEqual(str(m2).strip(), asm.strip())

if __name__ == '__main__':
    unittest.main()
