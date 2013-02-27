from binding import *
from src.namespace import llvm
from src.Pass import ImmutablePass

llvm.includes.add('llvm/TargetTransformInfo.h')

TargetTransformInfo = llvm.Class(ImmutablePass)
ScalarTargetTransformInfo = llvm.Class()
VectorTargetTransformInfo = llvm.Class()


@ScalarTargetTransformInfo
class ScalarTargetTransformInfo:
    delete = Destructor()

@VectorTargetTransformInfo
class VectorTargetTransformInfo:
    delete = Destructor()

@TargetTransformInfo
class TargetTransformInfo:
    new = Constructor(ptr(ScalarTargetTransformInfo),
                      ptr(VectorTargetTransformInfo))

