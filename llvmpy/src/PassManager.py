from binding import *
from .namespace import llvm

PassManagerBase = llvm.Class()
PassManager = llvm.Class(PassManagerBase)
FunctionPassManager = llvm.Class(PassManagerBase)

from .Pass import Pass
from .Module import Module
from .Value import Function


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

