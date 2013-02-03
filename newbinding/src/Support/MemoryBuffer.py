from binding import *
from ..namespace import llvm

MemoryBuffer = llvm.Class()

@MemoryBuffer
class MemoryBuffer:
    _include_ = 'llvm/Support/MemoryBuffer.h'

