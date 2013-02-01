from binding import *
from namespace import llvm

ScalarTargetTransformInfo = llvm.Class()
VectorTargetTransformInfo = llvm.Class()

@ScalarTargetTransformInfo
class ScalarTargetTransformInfo:
    delete = Destructor()

@VectorTargetTransformInfo
class VectorTargetTransformInfo:
    delete = Destructor()

