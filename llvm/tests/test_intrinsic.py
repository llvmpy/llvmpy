import unittest
import sys
import math
from llvm.core import (Module, Type, Function, Builder, Constant)
import llvm.core as lc
import llvm.ee as le
from .support import TestCase, tests, BITS

class TestIntrinsic(TestCase):
    def test_bswap(self):
        # setup a function and a builder
        mod    = Module.new('test')
        functy = Type.function(Type.int(), [])
        func   = mod.add_function(functy, "showme")
        block  = func.append_basic_block("entry")
        b      = Builder.new(block)

        # let's do bswap on a 32-bit integer using llvm.bswap
        val   = Constant.int(Type.int(), 0x42)
        bswap = Function.intrinsic(mod, lc.INTR_BSWAP, [Type.int()])

        bswap_res = b.call(bswap, [val])
        b.ret(bswap_res)

        # logging.debug(mod)

        # the output is:
        #
        #    ; ModuleID = 'test'
        #
        #    define void @showme() {
        #    entry:
        #      %0 = call i32 @llvm.bswap.i32(i32 42)
        #      ret i32 %0
        #    }

        # let's run the function
        ee = le.ExecutionEngine.new(mod)
        retval = ee.run_function(func, [])
        self.assertEqual(retval.as_int(), 0x42000000)

    def test_mysin(self):
        if sys.platform == 'win32' and BITS == 32:
            # float32 support is known to fail on 32-bit Windows
            return

        # mysin(x) = sqrt(1.0 - pow(cos(x), 2))
        mod     = Module.new('test')

        float   = Type.float()
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
        #logging.debug(mod)

#   ; ModuleID = 'test'
#
#   define void @showme() {
#   entry:
#       call i32 @llvm.bswap.i32( i32 42 )              ; <i32>:0 [#uses
#   }
#
#   declare i32 @llvm.bswap.i32(i32) nounwind readnone
#
#   define float @mysin(float %x) {
#   entry:
#       %cosx = call float @llvm.cos.f32( float %x )            ; <float
#       %cos2 = call float @llvm.powi.f32( float %cosx, i32 2 )
#       %onemc2 = sub float 1.000000e+00, %cos2         ; <float> [#uses
#       %sin = call float @llvm.sqrt.f32( float %onemc2 )
#       ret float %sin
#   }
#
#   declare float @llvm.sqrt.f32(float) nounwind readnone
#
#   declare float @llvm.powi.f32(float, i32) nounwind readnone
#
#   declare float @llvm.cos.f32(float) nounwind readnone

        # let's run the function

        from llvm.workaround.avx_support import detect_avx_support
        if not detect_avx_support():
            ee = le.EngineBuilder.new(mod).mattrs("-avx").create()
        else:
            ee = le.EngineBuilder.new(mod).create()

        arg = le.GenericValue.real(Type.float(), 1.234)
        retval = ee.run_function(mysin, [arg])

        golden = math.sin(1.234)
        answer = retval.as_real(Type.float())
        self.assertTrue(abs(answer-golden)/golden < 1e-5)

tests.append(TestIntrinsic)

if __name__ == '__main__':
    unittest.main()

