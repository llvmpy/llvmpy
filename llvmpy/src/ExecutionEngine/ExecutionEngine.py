from binding import *
from ..namespace import llvm
from ..Module import Module
from ..JITMemoryManager import JITMemoryManager
from ..Support.CodeGen import CodeGenOpt, Reloc, CodeModel
from ..DataLayout import DataLayout
from ..Value import Function, GlobalValue, BasicBlock, Constant
from ..GlobalVariable import GlobalVariable
from ..CodeGen.MachineCodeInfo import MachineCodeInfo
from ..GenericValue import GenericValue
from ..Type import Type

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

    addModule = Method(Void, ownedptr(Module))
    getDataLayout = Method(const(ownedptr(DataLayout)))
    _removeModule = Method(cast(Bool, bool), ptr(Module))
    _removeModule.realname = 'removeModule'
    @CustomPythonMethod
    def removeModule(self, module):
        if self._removeModule(module):
            capsule.obtain_ownership(module._capsule)
            return True
        return False

    FindFunctionNamed = Method(ptr(Function), cast(str, ConstCharPtr))
    getPointerToNamedFunction = Method(cast(VoidPtr, int),
                                       cast(str, StdString),
                                       cast(bool, Bool)).require_only(1)

    runStaticConstructorsDestructors = Method(Void,
                                              cast(Bool, bool), # is dtor
                                              )
    runStaticConstructorsDestructors |= Method(Void, ptr(Module),
                                              cast(Bool, bool))

    addGlobalMapping = Method(Void, ptr(GlobalValue), cast(int, VoidPtr))
    clearAllGlobalMappings = Method()
    clearGlobalMappingsFromModule = Method(Void, ptr(Module))
    updateGlobalMapping = Method(cast(VoidPtr, int),
                                 ptr(GlobalValue), cast(int, VoidPtr))

    getPointerToGlobalIfAvailable = Method(cast(VoidPtr, int), ptr(GlobalValue))
    getPointerToGlobal = Method(cast(VoidPtr, int), ptr(GlobalValue))
    getPointerToFunction = Method(cast(VoidPtr, int), ptr(Function))
    getPointerToBasicBlock = Method(cast(VoidPtr, int), ptr(BasicBlock))
    getPointerToFunctionOrStub = Method(cast(VoidPtr, int), ptr(Function))

    runJITOnFunction = Method(Void, ptr(Function), ptr(MachineCodeInfo))
    runJITOnFunction.require_only(1)

    getGlobalValueAtAddress = Method(const(ptr(GlobalValue)), cast(int, VoidPtr))

    StoreValueToMemory = Method(Void, ref(GenericValue), ptr(GenericValue),
                                ptr(Type))

    InitializeMemory = Method(Void, ptr(Constant), cast(int, VoidPtr))

    recompileAndRelinkFunction = Method(cast(int, VoidPtr), ptr(Function))

    freeMachineCodeForFunction = Method(Void, ptr(Function))
    getOrEmitGlobalVariable = Method(cast(int, VoidPtr), ptr(GlobalVariable))

    DisableLazyCompilation = Method(Void, cast(bool, Bool))
    isCompilingLazily = Method(cast(Bool, bool))
    isLazyCompilationDisabled = Method(cast(Bool, bool))
    DisableGVCompilation = Method(Void, cast(bool, Bool))
    isSymbolSearchingDisabled = Method(cast(Bool, bool))
    RegisterTable = Method(Void, ptr(Function), cast(int, VoidPtr))
    DeregisterTable = Method(Void, ptr(Function))
    DeregisterAllTables = Method()

    _runFunction = CustomMethod('ExecutionEngine_RunFunction',
                                PyObjectPtr, ptr(Function), PyObjectPtr)

    @CustomPythonMethod
    def runFunction(self, fn, args):
        from llvmpy import capsule
        unwrapped = list(map(capsule.unwrap, args))
        return self._runFunction(fn, tuple(unwrapped))

    finalizeObject = Method(Void)

