import unittest
import llvm.core as lc
import llvm.ee as le
from llvm.core import Type, Builder
from .support import TestCase, tests

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

    def test_ptx(self):
        if le.initialize_target('PTX', noraise=True):
            arch = 'ptx64'
        elif le.initialize_target('NVPTX', noraise=True):
            arch = 'nvptx64'
        else:
            return # skip this test

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

    def _build_bad_archname(self):
        with self.assertRaises(RuntimeError):
            le.TargetMachine.lookup("ain't no arch name")

tests.append(TestTargetMachines)

if __name__ == '__main__':
    unittest.main()

