from binding import *
from namespace import llvm

TargetMachine = llvm.Class()

@TargetMachine
class TargetMachine:
    _include_ = 'llvm/Target/TargetMachine.h'
    delete = Destructor()


