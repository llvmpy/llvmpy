from binding import *
from ..namespace import llvm
from ..BytesMemoryObject import MemoryObject
from ..Support.raw_ostream import raw_ostream

MCSubtargetInfo = llvm.Class()
MCDisassembler = llvm.Class()
MCInst = llvm.Class()
MCOperand = llvm.Class()

@MCSubtargetInfo
class MCSubtargetInfo:
    pass

@MCOperand
class MCOperand:
    pass

@MCInst
class MCInst:
    _include_ = "llvm/MC/MCInst.h"
    new = Constructor()

    size = Method(cast(Size_t, int))
    getNumOperands = Method(cast(Unsigned, int))

    getOperand = Method(const(ref(MCOperand)), cast(int, Unsigned))

@MCDisassembler
class MCDisassembler:
    _include_ = "llvm/MC/MCDisassembler.h"

    DecodeStatus = Enum('Fail', 'SoftFail', 'Success')

    getInstruction = CustomMethod('MCDisassembler_getInstruction', 
                                  PyObjectPtr,
                                  ref(MCInst),
                                  ref(MemoryObject),
                                  cast(int, Uint64)


)