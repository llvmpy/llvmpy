from binding import *
from src.namespace import llvm
from src.Pass import ImmutablePass

if LLVM_VERSION >= (3, 3):
    llvm.includes.add('llvm/Analysis/TargetTransformInfo.h')
else:
    llvm.includes.add('llvm/TargetTransformInfo.h')

TargetTransformInfo = llvm.Class(ImmutablePass)
ScalarTargetTransformInfo = llvm.Class()
VectorTargetTransformInfo = llvm.Class()


@ScalarTargetTransformInfo
class ScalarTargetTransformInfo:
    if LLVM_VERSION < (3, 3):
        delete = Destructor()

@VectorTargetTransformInfo
class VectorTargetTransformInfo:
    if LLVM_VERSION < (3, 3):
        delete = Destructor()

@TargetTransformInfo
class TargetTransformInfo:
    if LLVM_VERSION < (3, 3):
        new = Constructor(ptr(ScalarTargetTransformInfo),
                          ptr(VectorTargetTransformInfo))

