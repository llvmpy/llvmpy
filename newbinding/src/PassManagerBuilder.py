from binding import *
from namespace import llvm
from PassManager import PassManagerBase, FunctionPassManager
from TargetLibraryInfo import TargetLibraryInfo
from Pass import Pass

@llvm.Class()
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

    DisableSimplifyLibCalls = _attr_bool()
    DisableUnitAtATime = _attr_bool()
    DisableUnrollLoops = _attr_bool()
    Vectorize = _attr_bool()
    LoopVectorize = _attr_bool()

    LibraryInfo = Attr(getter=ownedptr(TargetLibraryInfo),
                       setter=ownedptr(TargetLibraryInfo))

    Inliner = Attr(getter=ownedptr(Pass),
                   setter=ownedptr(Pass))
