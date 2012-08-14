from llvm.core import *
from llvm.ee import TargetMachine, EngineBuilder, print_registered_targets
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

    def test_ptx(self):
        m, func = self._build_module()
        func.calling_convention = CC_PTX_KERNEL # set calling conv
        ptxtm = TargetMachine.lookup(arch='ptx64', cpu='compute_20',
                                     features='-double')
        self.assertTrue(ptxtm.triple)
        self.assertTrue(ptxtm.cpu)
        self.assertTrue(ptxtm.feature_string)
        ptxasm = ptxtm.emit_assembly(m).decode('utf-8')
        self.assertIn('foo', ptxasm)
        self.assertIn('map_f64_to_f32', ptxasm)
        self.assertIn('compute_10', ptxasm)

    def _build_module(self):
        m = Module.new('TestTargetMachines')

        fnty = Type.function(Type.void(), [])
        func = m.add_function(fnty, name='foo')

        bldr = Builder.new(func.append_basic_block('entry'))
        bldr.ret_void()
        m.verify()
        return m, func

if __name__ == '__main__':
    unittest.main()

