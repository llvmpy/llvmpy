import unittest
import sys
import math
from llvm.core import (Module, Type, Function, Builder)
import llvm.core as lc
import llvm.ee as le
from .support import TestCase, BITS, tests

class TestIntrinsicBasic(TestCase):

    def _build_module(self, float):
        mod     = Module.new('test')
        functy  = Type.function(float, [float])
        func    = mod.add_function(functy, "mytest%s" % float)
        block   = func.append_basic_block("entry")
        b       = Builder.new(block)
        return mod, func, b

    def _template(self, mod, func, pyfunc):
        float = func.type.pointee.return_type

        from llvm.workaround.avx_support import detect_avx_support
        if not detect_avx_support():
            ee = le.EngineBuilder.new(mod).mattrs("-avx").create()
        else:
            ee = le.EngineBuilder.new(mod).create()
        arg = le.GenericValue.real(float, 1.234)
        retval = ee.run_function(func, [arg])
        golden = pyfunc(1.234)
        answer = retval.as_real(float)
        self.assertTrue(abs(answer - golden) / golden < 1e-7)

    def test_sqrt_f32(self):
        float = Type.float()
        mod, func, b = self._build_module(float)
        intr = Function.intrinsic(mod, lc.INTR_SQRT, [float])
        b.ret(b.call(intr, func.args))
        self._template(mod, func, math.sqrt)

    def test_sqrt_f64(self):
        float = Type.double()
        mod, func, b = self._build_module(float)
        intr = Function.intrinsic(mod, lc.INTR_SQRT, [float])
        b.ret(b.call(intr, func.args))
        self._template(mod, func, math.sqrt)

    def test_cos_f32(self):
        if sys.platform == 'win32' and BITS == 32:
            # float32 support is known to fail on 32-bit Windows
            return
        float = Type.float()
        mod, func, b = self._build_module(float)
        intr = Function.intrinsic(mod, lc.INTR_COS, [float])
        b.ret(b.call(intr, func.args))
        self._template(mod, func, math.cos)

    def test_cos_f64(self):
        float = Type.double()
        mod, func, b = self._build_module(float)
        intr = Function.intrinsic(mod, lc.INTR_COS, [float])
        b.ret(b.call(intr, func.args))
        self._template(mod, func, math.cos)

    def test_sin_f32(self):
        if sys.platform == 'win32' and BITS == 32:
            # float32 support is known to fail on 32-bit Windows
            return
        float = Type.float()
        mod, func, b = self._build_module(float)
        intr = Function.intrinsic(mod, lc.INTR_SIN, [float])
        b.ret(b.call(intr, func.args))
        self._template(mod, func, math.sin)

    def test_sin_f64(self):
        float = Type.double()
        mod, func, b = self._build_module(float)
        intr = Function.intrinsic(mod, lc.INTR_SIN, [float])
        b.ret(b.call(intr, func.args))
        self._template(mod, func, math.sin)

    def test_powi_f32(self):
        float = Type.float()
        mod, func, b = self._build_module(float)
        intr = Function.intrinsic(mod, lc.INTR_POWI, [float])
        b.ret(b.call(intr, [func.args[0], lc.Constant.int(Type.int(), 2)]))
        self._template(mod, func, lambda x: x**2)

    def test_powi_f64(self):
        float = Type.double()
        mod, func, b = self._build_module(float)
        intr = Function.intrinsic(mod, lc.INTR_POWI, [float])
        b.ret(b.call(intr, [func.args[0], lc.Constant.int(Type.int(), 2)]))
        self._template(mod, func, lambda x: x**2)

tests.append(TestIntrinsicBasic)

if __name__ == '__main__':
    unittest.main()

