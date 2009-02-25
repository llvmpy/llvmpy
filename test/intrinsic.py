#!/usr/bin/env python

# This example shows how to use LLVM intrinsics.

from llvm.core import *
from llvm.ee import *

# setup a function and a builder
mod    = Module.new('test')
functy = Type.function(Type.void(), [])
func   = mod.add_function(functy, "showme")
block  = func.append_basic_block("entry")
b      = Builder.new(block)

# let's do bswap on a 32-bit integer using llvm.bswap
val   = Constant.int(Type.int(), 42)
bswap = Function.intrinsic(mod, INTR_BSWAP, [Type.int()])
b.call(bswap, [val])
print mod

# the output is:
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

# mysin(x) = sqrt(1.0 - pow(cos(x), 2))

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
onemc2 = b.sub(one, cos2, "onemc2")
sin  = b.call(sqrt, [onemc2], "sin")
b.ret(sin)
print mod

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
