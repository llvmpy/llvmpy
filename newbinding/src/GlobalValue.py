from binding import *
from namespace import llvm
from Constant import Constant

@llvm.Class(Constant)
class GlobalValue:
    _include_ = 'llvm/GlobalValue.h'

