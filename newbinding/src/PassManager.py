from binding import *
from namespace import llvm
from Pass import Pass
from Module import Module
from Function import Function

PassManagerBase = llvm.Class()
PassManager = llvm.Class(PassManagerBase)
FunctionPassManager = llvm.Class(PassManagerBase)

@PassManagerBase
class PassManagerBase:
    _include_ = 'llvm/PassManager.h'

    delete = Destructor()

    add = Method(Void, ownedptr(Pass))

@PassManager
class PassManager:
    new = Constructor()

    run = Method(cast(Bool, bool), ref(Module))


@FunctionPassManager
class FunctionPassManager:
    new = Constructor(ptr(Module))

    run = Method(cast(Bool, bool), ref(Function))

    doInitialization = Method(cast(Bool, bool))
    doFinalization = Method(cast(Bool, bool))

