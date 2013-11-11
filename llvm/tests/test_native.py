import unittest
import os
import sys
import shutil
import subprocess
import tempfile
from distutils.spawn import find_executable
from llvm.core import (Module, Type, Builder, Constant)
from .support import TestCase, IS_PY3K, tests, skip_if

@skip_if(sys.platform in ('win32', 'darwin'))
class TestNative(TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)


    def _make_module(self):
        m = Module.new('module1')
        m.add_global_variable(Type.int(), 'i')

        fty = Type.function(Type.int(), [])
        f = m.add_function(fty, name='main')

        bldr = Builder.new(f.append_basic_block('entry'))
        bldr.ret(Constant.int(Type.int(), 0xab))

        return m

    def _compile(self, src):
        cc = find_executable('cc')
        if not cc:
            return

        dst = os.path.join(self.tmpdir, 'llvmobj.out')
        s = subprocess.call([cc, '-o', dst, src])
        if s != 0:
            raise Exception("Cannot compile")

        s = subprocess.call([dst])
        self.assertEqual(s, 0xab)

    def test_assembly(self):
        #        if sys.platform == 'darwin':
        #            # skip this test on MacOSX for now
        #            return

        m = self._make_module()
        output = m.to_native_assembly()

        src = os.path.join(self.tmpdir, 'llvmasm.s')
        with open(src, 'wb') as fout:
            if IS_PY3K:
                fout.write(output.encode('utf-8'))
            else:
                fout.write(output)

        self._compile(src)

    def test_object(self):
        '''
        Note: Older Darwin with GCC will report missing _main symbol when
              compile the object file to an executable.
        '''
        m = self._make_module()
        output = m.to_native_object()

        src = os.path.join(self.tmpdir, 'llvmobj.o')
        with open(src, 'wb') as fout:
            fout.write(output)

        self._compile(src)

tests.append(TestNative)

if __name__ == '__main__':
    unittest.main()

