from binding import *
from namespace import llvm
from StringRef import StringRef
from Module import Module
from Function import Function

Pass = llvm.Class()
ModulePass = llvm.Class(Pass)
FunctionPass = llvm.Class(Pass)
ImmutablePass = llvm.Class(ModulePass)


@Pass
class Pass:
    _include_ = 'llvm/Pass.h'

    delete = Destructor()
    getPassName = Method(cast(StringRef, str))


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

