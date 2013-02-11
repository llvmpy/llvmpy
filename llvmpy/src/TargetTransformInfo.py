from binding import *
from namespace import llvm

llvm.includes.add('llvm/TargetTransformInfo.h')

ScalarTargetTransformInfo = llvm.Class()
VectorTargetTransformInfo = llvm.Class()

@ScalarTargetTransformInfo
class ScalarTargetTransformInfo:
    delete = Destructor()

@VectorTargetTransformInfo
class VectorTargetTransformInfo:
    delete = Destructor()

