from binding import *
from .namespace import llvm
from .Value import GlobalValue, Constant, Function, Argument, Value
from .BasicBlock import BasicBlock
from .Attributes import Attributes
from .Type import Type
from .DerivedTypes import FunctionType
from .LLVMContext import LLVMContext
from .CallingConv import CallingConv

@Function
class Function:
    _include_ = 'llvm/Function.h'
    _downcast_  = GlobalValue, Constant, Value

    getReturnType = Method(ptr(Type))
    getFunctionType = Method(ptr(FunctionType))
    getContext = Method(ref(LLVMContext))
    isVarArg = Method(cast(Bool, bool))
    getIntrinsicID = Method(cast(Unsigned, int))
    isIntrinsic = Method(cast(Bool, bool))

    getCallingConv = Method(CallingConv.ID)
    setCallingConv = Method(Void, CallingConv.ID)

    hasGC = Method(cast(bool, Bool))
    getGC = Method(cast(ConstCharPtr, str))
    setGC = Method(Void, cast(str, ConstCharPtr))


    getArgumentList = CustomMethod('Function_getArgumentList', PyObjectPtr)
    getBasicBlockList = CustomMethod('Function_getBasicBlockList', PyObjectPtr)
    getEntryBlock = Method(ref(BasicBlock))

    copyAttributesFrom = Method(Void, ptr(GlobalValue))

    setDoesNotThrow = Method()
    doesNotThrow = Method(cast(Bool, bool))
    setDoesNotReturn = Method()
    doesNotReturn = Method(cast(Bool, bool))
    setOnlyReadsMemory = Method()
    onlyReadsMemory = Method(cast(Bool, bool))
    setDoesNotAccessMemory = Method()
    doesNotAccessMemory = Method(cast(Bool, bool))

    deleteBody = Method()
    viewCFG = Method()
    viewCFGOnly = Method()

    addFnAttr = Method(Void, Attributes.AttrVal)
    removeFnAttr = Method(Void, ref(Attributes))

    eraseFromParent = Method()
    eraseFromParent.disowning = True

