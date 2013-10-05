import unittest
import llvm.core as lc
import llvm.ee as le
from llvm.core import Type, Builder
from .support import TestCase, tests, skip_if

# Check PTX backend
if le.initialize_target('PTX', noraise=True):
    PTX_ARCH = 'ptx64'
elif le.initialize_target('NVPTX', noraise=True):
    PTX_ARCH = 'nvptx64'
else:
    PTX_ARCH = None

class TestTargetMachines(TestCase):
    '''Exercise target machines

    Require PTX backend
    '''
    def test_native(self):
        m, _ = self._build_module()
        tm = le.EngineBuilder.new(m).select_target()

        self.assertTrue(tm.target_name)
        self.assertTrue(tm.target_data)
        self.assertTrue(tm.target_short_description)
        self.assertTrue(tm.triple)
        self.assertIn('foo', tm.emit_assembly(m))
        self.assertTrue(le.get_host_cpu_name())

    @skip_if(not PTX_ARCH, msg='LLVM is not compiled with PTX enabled')
    def test_ptx(self):
        arch = PTX_ARCH
        print(arch)
        m, func = self._build_module()
        func.calling_convention = lc.CC_PTX_KERNEL # set calling conv
        ptxtm = le.TargetMachine.lookup(arch=arch, cpu='sm_20')
        self.assertTrue(ptxtm.triple)
        self.assertTrue(ptxtm.cpu)
        ptxasm = ptxtm.emit_assembly(m)
        self.assertIn('foo', ptxasm)
        if arch == 'nvptx64':
            self.assertIn('.address_size 64', ptxasm)
        self.assertIn('sm_20', ptxasm)

    def _build_module(self):
        m = lc.Module.new('TestTargetMachines')

        fnty = Type.function(Type.void(), [])
        func = m.add_function(fnty, name='foo')

        bldr = Builder.new(func.append_basic_block('entry'))
        bldr.ret_void()
        m.verify()
        return m, func


tests.append(TestTargetMachines)

if __name__ == '__main__':
    unittest.main()

