import unittest
import math
from llvm.core import (Module, Type, Function, Builder,
                       Constant)
from llvm.ee import EngineBuilder
import llvm.core as lc
import llvm.ee as le
from llvm.workaround.avx_support import detect_avx_support
from .support import TestCase, tests, skip_if_not_intel_cpu, skip_if

@skip_if_not_intel_cpu
class TestCPUSupport(TestCase):

    def _build_test_module(self):
        mod     = Module.new('test')

        float   = Type.double()
        mysinty = Type.function( float, [float] )
        mysin   = mod.add_function(mysinty, "mysin")
        block   = mysin.append_basic_block("entry")
        b       = Builder.new(block)

        sqrt = Function.intrinsic(mod, lc.INTR_SQRT, [float])
        pow  = Function.intrinsic(mod, lc.INTR_POWI, [float])
        cos  = Function.intrinsic(mod, lc.INTR_COS,  [float])

        mysin.args[0].name = "x"
        x    = mysin.args[0]
        one  = Constant.real(float, "1")
        cosx = b.call(cos, [x], "cosx")
        cos2 = b.call(pow, [cosx, Constant.int(Type.int(), 2)], "cos2")
        onemc2 = b.fsub(one, cos2, "onemc2") # Should use fsub
        sin  = b.call(sqrt, [onemc2], "sin")
        b.ret(sin)
        return mod, mysin

    def _template(self, mattrs):
        mod, func = self._build_test_module()
        ee = self._build_engine(mod, mattrs=mattrs)
        arg = le.GenericValue.real(Type.double(), 1.234)
        retval = ee.run_function(func, [arg])

        golden = math.sin(1.234)
        answer = retval.as_real(Type.double())
        self.assertTrue(abs(answer-golden)/golden < 1e-5)


    def _build_engine(self, mod, mattrs):
        if mattrs:
            return EngineBuilder.new(mod).mattrs(mattrs).create()
        else:
            return EngineBuilder.new(mod).create()

    def test_cpu_support2(self):
        features = 'sse3', 'sse41', 'sse42', 'avx'
        mattrs = ','.join(map(lambda s: '-%s' % s, features))
        print('disable mattrs', mattrs)
        self._template(mattrs)

    def test_cpu_support3(self):
        features = 'sse41', 'sse42', 'avx'
        mattrs = ','.join(map(lambda s: '-%s' % s, features))
        print('disable mattrs', mattrs)
        self._template(mattrs)

    def test_cpu_support4(self):
        features = 'sse42', 'avx'
        mattrs = ','.join(map(lambda s: '-%s' % s, features))
        print('disable mattrs', mattrs)
        self._template(mattrs)

    def test_cpu_support5(self):
        features = 'avx',
        mattrs = ','.join(map(lambda s: '-%s' % s, features))
        print('disable mattrs', mattrs)
        self._template(mattrs)

    @skip_if(not detect_avx_support(), msg="no AVX support")
    def test_cpu_support6(self):
        features = []
        mattrs = ','.join(map(lambda s: '-%s' % s, features))
        print('disable mattrs', mattrs)
        self._template(mattrs)

tests.append(TestCPUSupport)

if __name__ == '__main__':
    unittest.main()

