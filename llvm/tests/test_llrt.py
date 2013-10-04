import unittest
import llvm.core as lc
import llvm.ee as le
from .support import TestCase, tests

class TestLLRT(TestCase):
    def test_llrt_divmod(self):
        from llvm import llrt
        m = lc.Module.new('testllrt')
        longlong = lc.Type.int(64)
        lfunc = m.add_function(lc.Type.function(longlong, [longlong, longlong]), 'foo')
        bldr = lc.Builder.new(lfunc.append_basic_block(''))
        bldr.ret(bldr.udiv(*lfunc.args))

        llrt.replace_divmod64(lfunc)

        rt = llrt.LLRT()
        rt.install_symbols()

        engine = le.EngineBuilder.new(m).create()
        pointer = engine.get_pointer_to_function(lfunc)

        from ctypes import CFUNCTYPE, c_uint64
        func = CFUNCTYPE(c_uint64, c_uint64, c_uint64)(pointer)
        a, b = 98342, 2231
        self.assertEqual(func(98342, 2231), 98342 // 2231)

        rt.uninstall_symbols()

tests.append(TestLLRT)

if __name__ == '__main__':
    unittest.main()

