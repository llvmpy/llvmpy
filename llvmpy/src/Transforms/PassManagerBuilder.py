from binding import *
from ..namespace import llvm

PassManagerBuilder = llvm.Class()

from src.PassManager import PassManagerBase, FunctionPassManager
from src.Target.TargetLibraryInfo import TargetLibraryInfo
from src.Pass import Pass

@PassManagerBuilder
class PassManagerBuilder:
    _include_ = 'llvm/Transforms/IPO/PassManagerBuilder.h'

    new = Constructor()
    delete = Destructor()

    populateFunctionPassManager = Method(Void, ref(FunctionPassManager))
    populateModulePassManager = Method(Void, ref(PassManagerBase))
    populateLTOPassManager = Method(Void,
                                    ref(PassManagerBase),
                                    cast(bool, Bool),
                                    cast(bool, Bool),
                                    cast(bool, Bool)).require_only(3)

    def _attr_int():
        return Attr(getter=cast(Unsigned, int),
                    setter=cast(int, Unsigned))

    OptLevel = _attr_int()
    SizeLevel = _attr_int()

    def _attr_bool():
        return Attr(getter=cast(Bool, bool),
                    setter=cast(bool, Bool))

    if LLVM_VERSION <= (3, 3):
        DisableSimplifyLibCalls = _attr_bool()

    DisableUnitAtATime = _attr_bool()
    DisableUnrollLoops = _attr_bool()
    if LLVM_VERSION >= (3, 3):
        BBVectorize = _attr_bool()
        SLPVectorize = _attr_bool()
    else:
        Vectorize = _attr_bool()
    LoopVectorize = _attr_bool()

    LibraryInfo = Attr(getter=ownedptr(TargetLibraryInfo),
                       setter=ownedptr(TargetLibraryInfo))

    Inliner = Attr(getter=ownedptr(Pass),
                   setter=ownedptr(Pass))
