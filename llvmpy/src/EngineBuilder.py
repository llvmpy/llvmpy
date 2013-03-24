from binding import *
from .namespace import llvm
from .Module import Module
from .JITMemoryManager import JITMemoryManager
from .Support.CodeGen import CodeGenOpt, Reloc, CodeModel
from .ADT.StringRef import StringRef
from .ExecutionEngine.ExecutionEngine import ExecutionEngine
from .Target.TargetMachine import TargetMachine
from .ADT.Triple import Triple

EngineBuilder = llvm.Class()

EngineKind = llvm.Namespace('EngineKind')
Kind = EngineKind.Enum('Kind', 'JIT', 'Interpreter')

@EngineBuilder
class EngineBuilder:
    new = Constructor(ownedptr(Module))
    delete = Destructor()

    def _setter(*args):
        return Method(ref(EngineBuilder), *args)

    setEngineKind = _setter(Kind)
    setJITMemoryManager = _setter(ptr(JITMemoryManager))
# FIXME
#    setErrorStr = CustomMethod('EngineBuilder_setErrorStr',
#                                PyObjectPtr, PyObjectPtr)

    setOptLevel = _setter(CodeGenOpt.Level)
    #setTargetOptions =
    setRelocationModel = _setter(Reloc.Model)
    setCodeModel = _setter(CodeModel.Model)
    setAllocateGVsWithCode = _setter(cast(bool, Bool))
    setMArch = _setter(cast(str, StringRef))
    setMCPU = _setter(cast(str, StringRef))
    setUseMCJIT = _setter(cast(bool, Bool))
    _setMAttrs = CustomMethod('EngineBuilder_setMAttrs',
                              PyObjectPtr, PyObjectPtr)
    @CustomPythonMethod
    def setMAttrs(self, attrs):
        attrlist = list(str(a) for a in attrs)
        return self._setMAttrs(attrlist)

    create = Method(ptr(ExecutionEngine),
                    ownedptr(TargetMachine)).require_only(0)

    _selectTarget0 = Method(ptr(TargetMachine))
    _selectTarget0.realname = 'selectTarget'

    _selectTarget1 = CustomMethod('EngineBuilder_selectTarget',
                                 PyObjectPtr,
                                 const(ref(Triple)), cast(str, StringRef),
                                 cast(str, StringRef), PyObjectPtr)

    @CustomPythonMethod
    def selectTarget(self, *args):
        if not args:
            return self._selectTarget0()
        else:
            return self._selectTarget1(*args)

