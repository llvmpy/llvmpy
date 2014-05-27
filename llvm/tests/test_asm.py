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

    def create_module(self):
        # create a module
        m = Module.new('module1')
        m.add_global_variable(Type.int(), 'i')
        return m

    def test_asm_roundtrip(self):
        m = self.create_module()

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

    def test_bitcode_roundtrip(self):
        m = self.create_module()

        testasm_bc = os.path.join(self.tmpdir, 'testasm.bc')
        with open(testasm_bc, "wb") as fout:
            m.to_bitcode(fout)

        # read it back into a module
        with open(testasm_bc, "rb") as fin:
            m2 = Module.from_bitcode(fin)
            # The default `m.id` is '<string>'.
            m2.id = m.id # Copy the name from `m`

        with open(testasm_bc, "rb") as fin:
            m3 = Module.from_bitcode(fin.read())
            # The default `m.id` is '<string>'.
            m3.id = m.id # Copy the name from `m`

        self.assertEqual(str(m2).strip(), str(m).strip())
        self.assertEqual(str(m3).strip(), str(m).strip())

    def test_to_bitcode(self):
        m = self.create_module()
        testasm_bc = os.path.join(self.tmpdir, 'testasm.bc')
        with open(testasm_bc, "wb") as fout:
            m.to_bitcode(fout)
        with open(testasm_bc, "rb") as fin:
            self.assertEqual(fin.read(), m.to_bitcode())


tests.append(TestAsm)

if __name__ == '__main__':
    unittest.main()
