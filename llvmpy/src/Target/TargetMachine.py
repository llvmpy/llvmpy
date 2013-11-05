from binding import *
from src.namespace import llvm

TargetMachine = llvm.Class()

from src.Support.TargetRegistry import Target
from src.ADT.StringRef import StringRef
from src.Support.CodeGen import CodeModel, TLSModel, CodeGenOpt, Reloc
from src.GlobalValue import GlobalValue
from src.DataLayout import DataLayout
if LLVM_VERSION >= (3, 4):
    from src.MC import MCAsmInfo, \
                       TargetInstrInfo, \
                       TargetSubtargetInfo, \
                       TargetRegisterInfo

if LLVM_VERSION < (3, 3):
    from src.TargetTransformInfo import (ScalarTargetTransformInfo,
                                         VectorTargetTransformInfo)
from src.PassManager import PassManagerBase
from src.Support.FormattedStream import formatted_raw_ostream

@TargetMachine
class TargetMachine:
    _include_ = 'llvm/Target/TargetMachine.h'

    CodeGenFileType = Enum('''
                           CGFT_AssemblyFile
                           CGFT_ObjectFile
                           CGFT_Null''')

    delete = Destructor()

    getTarget = Method(const(ref(Target)))

    getTargetTriple = Method(cast(StringRef, str))
    getTargetCPU = Method(cast(StringRef, str))
    getTargetFeatureString = Method(cast(StringRef, str))

    getRelocationModel = Method(Reloc.Model)
    getCodeModel = Method(CodeModel.Model)
    getTLSModel = Method(TLSModel.Model, ptr(GlobalValue))
    getOptLevel = Method(CodeGenOpt.Level)

    hasMCUseDwarfDirectory = Method(cast(Bool, bool))
    setMCUseDwarfDirectory = Method(Void, cast(bool, Bool))

    getDataLayout = Method(const(ownedptr(DataLayout)))

    if LLVM_VERSION < (3, 3):
        getScalarTargetTransformInfo = Method(const(
                                          ownedptr(ScalarTargetTransformInfo)))
        getVectorTargetTransformInfo = Method(const(
                                          ownedptr(VectorTargetTransformInfo)))

    else:
        addAnalysisPasses = Method(Void, ref(PassManagerBase))

    addPassesToEmitFile = Method(cast(bool, Bool),
                                 ref(PassManagerBase),
                                 ref(formatted_raw_ostream),
                                 CodeGenFileType,
                                 cast(bool, Bool)
                                 ).require_only(3)

    if LLVM_VERSION >= (3, 4):
        getSubtargetImpl = Method(const(ownedptr(TargetSubtargetInfo)))

        getMCAsmInfo = Method(const(ownedptr(MCAsmInfo)))

        getInstrInfo = Method(const(ownedptr(TargetInstrInfo)))

        getRegisterInfo = Method(const(ownedptr(TargetRegisterInfo)))

