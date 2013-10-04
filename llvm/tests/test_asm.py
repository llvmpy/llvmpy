import os
import unittest
import tempfile
import shutil
from llvm.core import Module, Type
from .support import TestCase, tests

class TestAsm(TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_asm(self):
        # create a module
        m = Module.new('module1')
        m.add_global_variable(Type.int(), 'i')

        # write it's assembly representation to a file
        asm = str(m)

        testasm_ll = os.path.join(self.tmpdir, 'testasm.ll')
        with open(testasm_ll, "w") as fout:
            fout.write(asm)

        # read it back into a module
        with open(testasm_ll) as fin:
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

        testasm_bc = os.path.join(self.tmpdir, 'testasm.bc')
        with open(testasm_bc, "wb") as fout:
            m.to_bitcode(fout)

        # read it back into a module
        with open(testasm_bc, "rb") as fin:
            m2 = Module.from_bitcode(fin)
            # The default `m.id` is '<string>'.
            m2.id = m.id # Copy the name from `m`

        self.assertEqual(str(m2).strip(), asm.strip())

tests.append(TestAsm)

if __name__ == '__main__':
    unittest.main()
