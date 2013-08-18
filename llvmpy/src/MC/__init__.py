from binding import *
from ..namespace import llvm
from ..Support.StringRefMemoryObject import MemoryObject
from ..Support.raw_ostream import raw_ostream

MCSubtargetInfo = llvm.Class()
MCDisassembler = llvm.Class()
MCInst = llvm.Class()
MCOperand = llvm.Class()
MCExpr = llvm.Class()
MCAsmInfo = llvm.Class()
MCRegisterInfo = llvm.Class()
MCInstrInfo = llvm.Class()
MCInstrAnalysis = llvm.Class()
MCInstPrinter = llvm.Class()

TargetSubtargetInfo = llvm.Class(MCSubtargetInfo)
TargetInstrInfo = llvm.Class(MCInstrInfo)

@MCSubtargetInfo
class MCSubtargetInfo:
    pass

@TargetSubtargetInfo
class TargetSubtargetInfo:
    _include_ = 'llvm/Target/TargetSubtargetInfo.h'

@MCExpr
class MCExpr:
    _include_ = "llvm/MC/MCExpr.h"

    ExprKind = Enum('Binary', 'Constant', 'SymbolRef', 'Unary', 'Target')
    getKind = Method(ExprKind)

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

MCOperand.getInst = Method(const(ptr(MCInst)))

@MCAsmInfo
class MCAsmInfo:
    _include_ = "llvm/MC/MCAsmInfo.h"

    getAssemblerDialect = Method(cast(Unsigned, int))
    getMinInstAlignment = Method(cast(Unsigned, int))
    isLittleEndian = Method(cast(Bool, bool))

@MCRegisterInfo
class MCRegisterInfo:
    _include_ = "llvm/MC/MCRegisterInfo.h"

    getName = Method(cast(ConstCharPtr, str), cast(int, Unsigned))

@MCInstrInfo
class MCInstrInfo:
    _include_ = "llvm/MC/MCInstrInfo.h"

@TargetInstrInfo
class TargetInstrInfo:
    _include_ = 'llvm/Target/TargetInstrInfo.h'

@MCInstrAnalysis
class MCInstrAnalysis:
    _include_ = "llvm/MC/MCInstrAnalysis.h"

@MCInstPrinter
class MCInstPrinter:
    _include_ = "llvm/MC/MCInstPrinter.h"

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

