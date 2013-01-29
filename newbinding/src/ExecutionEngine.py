from binding import *
from namespace import llvm
from Module import Module
from JITMemoryManager import JITMemoryManager
from CodeGen import CodeGenOpt, Reloc, CodeModel
from DataLayout import DataLayout

ExecutionEngine = llvm.Class()

@ExecutionEngine
class ExecutionEngine:
    _include_ = ('llvm/ExecutionEngine/ExecutionEngine.h',
                 'llvm/ExecutionEngine/JIT.h') # force linking of jit

    delete = Destructor()
    
    create = CustomStaticMethod('ExecutionEngine_create',
                                ptr(ExecutionEngine),
                                ownedptr(Module), cast(bool, Bool),
                                PyObjectPtr, CodeGenOpt.Level,
                                cast(bool, Bool)).require_only(1)

    createJIT = CustomStaticMethod('ExecutionEngine_createJIT',
                                   ptr(ExecutionEngine),
                                   ownedptr(Module), PyObjectPtr,
                                   ptr(JITMemoryManager),
                                   CodeGenOpt.Level,
                                   cast(bool, Bool),
                                   Reloc.Model,
                                   CodeModel.Model).require_only(1)

    addModule = Method(Void, ptr(Module))
    getDataLayout = Method(const(ownedptr(DataLayout)))
    removeModule = Method(cast(Bool, bool), ptr(Module))
