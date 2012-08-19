from llvm.core import *
from llvm.ee import *
import unittest

class TestTargetMachines(unittest.TestCase):
    '''Exercise target machines

    Require PTX backend
    '''
    def test_native(self):
        m, _ = self._build_module()

        tm = EngineBuilder.new(m).select_target()

        self.assertTrue(tm.target_name)
        self.assertTrue(tm.target_data)
        self.assertTrue(tm.target_short_description)
        self.assertTrue(tm.triple)
        self.assertIn('foo', tm.emit_assembly(m).decode('utf-8'))
        self.assertTrue(get_host_cpu_name())

    def test_ptx(self):
        if HAS_PTX:
            arch = 'ptx64'
        elif HAS_NVPTX:
            arch = 'nvptx64'
        else:
            return # skip this test
        m, func = self._build_module()
        func.calling_convention = CC_PTX_KERNEL # set calling conv
        ptxtm = TargetMachine.lookup(arch=arch, cpu='compute_20')
        self.assertTrue(ptxtm.triple)
        self.assertTrue(ptxtm.cpu)
        ptxasm = ptxtm.emit_assembly(m).decode('utf-8')
        self.assertIn('foo', ptxasm)
        if HAS_NVPTX:
            self.assertIn('.address_size 64', ptxasm)
        self.assertIn('compute_20', ptxasm)

    def _build_module(self):
        m = Module.new('TestTargetMachines')

        fnty = Type.function(Type.void(), [])
        func = m.add_function(fnty, name='foo')

        bldr = Builder.new(func.append_basic_block('entry'))
        bldr.ret_void()
        m.verify()
        return m, func

    def _build_bad_archname(self):
        with self.assertRaises(RuntimeError):
            tm = TargetMachine.lookup("ain't no arch name")


if __name__ == '__main__':
    unittest.main()

