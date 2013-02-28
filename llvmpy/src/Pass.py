from binding import *
from .namespace import llvm

Pass = llvm.Class()
ModulePass = llvm.Class(Pass)
FunctionPass = llvm.Class(Pass)
ImmutablePass = llvm.Class(ModulePass)

from .ADT.StringRef import StringRef
from .Module import Module
from .Value import Function

@Pass
class Pass:
    _include_ = 'llvm/Pass.h'

    delete = Destructor()
    getPassName = Method(cast(StdString, str))
    dump = Method()

@ModulePass
class ModulePass:
    runOnModule = Method(cast(Bool, bool), ref(Module))


@FunctionPass
class FunctionPass:
    doInitialization = Method(cast(Bool, bool), ref(Module))
    doFinalization = Method(cast(Bool, bool), ref(Module))


@ImmutablePass
class ImmutablePass:
    pass

