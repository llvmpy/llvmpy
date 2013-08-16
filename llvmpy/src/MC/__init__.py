from binding import *
from ..namespace import llvm
from ..BytesMemoryObject import MemoryObject
from ..Support.raw_ostream import raw_ostream

MCSubtargetInfo = llvm.Class()
MCDisassembler = llvm.Class()
MCInst = llvm.Class()
MCOperand = llvm.Class()
MCExpr = llvm.Class()
MCAsmInfo = llvm.Class()

@MCSubtargetInfo
class MCSubtargetInfo:
    pass

@MCExpr
class MCExpr:
    _include_ = "llvm/MC/MCExpr.h"

@MCOperand
class MCOperand:
    _include_ = "llvm/MC/MCInst.h"

    isValid = Method(cast(Bool, bool))
    isReg = Method(cast(Bool, bool))
    isImm = Method(cast(Bool, bool))
    isFPImm = Method(cast(Bool, bool))
    isExpr = Method(cast(Bool, bool))
    isInst = Method(cast(Bool, bool))

    getReg = Method(cast(Unsigned, int))
    getImm = Method(cast(Int64, int))
    getFPImm = Method(cast(Double, float))
    getExpr = Method(const(ptr(MCExpr)))


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

@MCAsmInfo
class MCAsmInfo:
    _include_ = "llvm/MC/MCAsmInfo.h"
