#this file is not processed unless the llvm library is
#version 3.4 or higher. see llvmpy/__init__.py for details.
from binding import *
from ..namespace import llvm
from ..Support.StringRefMemoryObject import MemoryObject
from ..Support.raw_ostream import raw_ostream
from src.ADT.StringRef import StringRef

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
MCInstrDesc = llvm.Class()

TargetSubtargetInfo = llvm.Class(MCSubtargetInfo)
TargetInstrInfo = llvm.Class(MCInstrInfo)
TargetRegisterInfo = llvm.Class(MCRegisterInfo)

@MCInstrDesc
class MCInstrDesc:
    _include_ = "llvm/MC/MCInstrDesc.h"

    TSFlags = Attr(getter=cast(Uint64, int), setter=cast(int, Uint64))
    getFlags = Method(cast(Unsigned, int))
    getOpcode = Method(cast(Unsigned, int))

    def _ret_bool():
        return Method(cast(Bool, bool))

    isReturn = _ret_bool()
    isCall = _ret_bool()
    isBarrier = _ret_bool()
    isBranch = _ret_bool()
    isTerminator = _ret_bool()
    isIndirectBranch = _ret_bool()
    isConditionalBranch = _ret_bool()
    isUnconditionalBranch = _ret_bool()


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
    getExpr = Method(const(ownedptr(MCExpr)))

@MCInst
class MCInst:
    _include_ = "llvm/MC/MCInst.h"
    new = Constructor()

    size = Method(cast(Size_t, int))
    getNumOperands = Method(cast(Unsigned, int))

    getOperand = Method(const(ref(MCOperand)), cast(int, Unsigned))

    getOpcode = Method(cast(Unsigned, int))

MCOperand.getInst = Method(const(ownedptr(MCInst)))

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

@TargetRegisterInfo
class TargetRegisterInfo:
    _include_ = "llvm/Target/TargetRegisterInfo.h"

@MCInstrInfo
class MCInstrInfo:
    _include_ = "llvm/MC/MCInstrInfo.h"

    get = Method(const(ref(MCInstrDesc)), cast(int, Unsigned))

@TargetInstrInfo
class TargetInstrInfo:
    _include_ = 'llvm/Target/TargetInstrInfo.h'

@MCInstrAnalysis
class MCInstrAnalysis:
    _include_ = "llvm/MC/MCInstrAnalysis.h"


    def _take_mcinst_ret_bool():
        return Method(cast(Bool, bool), const(ref(MCInst)))

    isBranch = _take_mcinst_ret_bool()
    isConditionalBranch = _take_mcinst_ret_bool()
    isUnconditionalBranch = _take_mcinst_ret_bool()
    isIndirectBranch = _take_mcinst_ret_bool()
    isCall = _take_mcinst_ret_bool()
    isReturn = _take_mcinst_ret_bool()
    isTerminator = _take_mcinst_ret_bool()

@MCInstPrinter
class MCInstPrinter:
    _include_ = "llvm/MC/MCInstPrinter.h"

    printInst = Method(Void,
                       const(ptr(MCInst)),  #MI
                       ref(raw_ostream),    #OS
                       cast(str, StringRef) #Annot
                       )

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

