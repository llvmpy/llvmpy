from binding import *
from ..namespace import llvm

MCSubtargetInfo = llvm.Class()
MCDisassembler = llvm.Class()

@MCSubtargetInfo
class MCSubtargetInfo:
    pass


@MCDisassembler
class MCDisassembler:
    pass
