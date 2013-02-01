from binding import *
from namespace import llvm
from StringRef import StringRef
from CodeGen import CodeModel, TLSModel, CodeGenOpt, Reloc
from GlobalValue import GlobalValue
from Target import Target
from DataLayout import DataLayout
from TargetTransformInfo import (ScalarTargetTransformInfo,
                                 VectorTargetTransformInfo)

TargetMachine = llvm.Class()

@TargetMachine
class TargetMachine:
    _include_ = 'llvm/Target/TargetMachine.h'
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
    getScalarTargetTransformInfo = Method(const(
                                         ownedptr(ScalarTargetTransformInfo)))
    getVectorTargetTransformInfo = Method(const(
                                         ownedptr(VectorTargetTransformInfo)))
