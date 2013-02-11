from binding import *
from ..namespace import llvm

MachineCodeInfo = llvm.Class()

@MachineCodeInfo
class MachineCodeInfo:
    _include_ = 'llvm/CodeGen/MachineCodeInfo.h'
    setSize = Method(Void, cast(int, Size_t))
    setAddress = Method(Void, cast(int, VoidPtr))
    size = Method(cast(Size_t, int))
    address = Method(cast(VoidPtr, int))

