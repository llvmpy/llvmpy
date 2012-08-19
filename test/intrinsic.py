#!/usr/bin/env python

# This example shows how to use LLVM intrinsics.

from llvm.core import *
from llvm.ee import *

import logging
import unittest
import math

class TestIntrinsic(unittest.TestCase):
    def test_bswap(self):
        # setup a function and a builder
        mod    = Module.new('test')
        functy = Type.function(Type.int(), [])
        func   = mod.add_function(functy, "showme")
        block  = func.append_basic_block("entry")
        b      = Builder.new(block)

        # let's do bswap on a 32-bit integer using llvm.bswap
        val   = Constant.int(Type.int(), 0x42)
        bswap = Function.intrinsic(mod, INTR_BSWAP, [Type.int()])

        bswap_res = b.call(bswap, [val])
        b.ret(bswap_res)

        # see the generated IR
        logging.debug(mod)

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
        ee = ExecutionEngine.new(mod)
        retval = ee.run_function(func, [])
        self.assertEqual(retval.as_int(), 0x42000000)


    def test_mysin(self):
        # mysin(x) = sqrt(1.0 - pow(cos(x), 2))
        mod     = Module.new('test')

        float   = Type.float()
        mysinty = Type.function( float, [float] )
        mysin   = mod.add_function(mysinty, "mysin")
        block   = mysin.append_basic_block("entry")
        b       = Builder.new(block)

        sqrt = Function.intrinsic(mod, INTR_SQRT, [float])
        pow  = Function.intrinsic(mod, INTR_POWI, [float])
        cos  = Function.intrinsic(mod, INTR_COS,  [float])

        mysin.args[0].name = "x"
        x    = mysin.args[0]
        one  = Constant.real(float, "1")
        cosx = b.call(cos, [x], "cosx")
        cos2 = b.call(pow, [cosx, Constant.int(Type.int(), 2)], "cos2")
        onemc2 = b.fsub(one, cos2, "onemc2") # Should use fsub
        sin  = b.call(sqrt, [onemc2], "sin")
        b.ret(sin)

        logging.debug(mod)

        #
        #   ; ModuleID = 'test'
        #
        #   define void @showme() {
        #   entry:
        #   	call i32 @llvm.bswap.i32( i32 42 )		; <i32>:0 [#uses=0]
        #   }
        #
        #   declare i32 @llvm.bswap.i32(i32) nounwind readnone
        #
        #   define float @mysin(float %x) {
        #   entry:
        #   	%cosx = call float @llvm.cos.f32( float %x )		; <float> [#uses=1]
        #   	%cos2 = call float @llvm.powi.f32( float %cosx, i32 2 )		; <float> [#uses=1]
        #   	%onemc2 = sub float 1.000000e+00, %cos2		; <float> [#uses=1]
        #   	%sin = call float @llvm.sqrt.f32( float %onemc2 )		; <float> [#uses=1]
        #   	ret float %sin
        #   }
        #
        #   declare float @llvm.sqrt.f32(float) nounwind readnone
        #
        #   declare float @llvm.powi.f32(float, i32) nounwind readnone
        #
        #   declare float @llvm.cos.f32(float) nounwind readnone
        #

        # let's run the function
        ee = ExecutionEngine.new(mod)
        arg = GenericValue.real(Type.float(), 1.234)
        retval = ee.run_function(mysin, [arg])

        golden = math.sin(1.234)
        answer = retval.as_real(Type.float())
        self.assertTrue(abs(answer-golden)/golden < 1e-5)


if __name__ == '__main__':
    unittest.main()

