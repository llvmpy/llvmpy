from binding import *
from .namespace import llvm
from .Value import GlobalValue, Constant, Function, Argument, Value
from .Module import Module
from .BasicBlock import BasicBlock
from .ValueSymbolTable import ValueSymbolTable
if LLVM_VERSION >= (3, 3):
    from .Attributes import Attribute, AttributeSet
else:
    from .Attributes import Attributes
from .Type import Type
from .DerivedTypes import FunctionType
from .LLVMContext import LLVMContext
from .CallingConv import CallingConv

@Function
class Function:
    if LLVM_VERSION >= (3, 3):
        _include_ = 'llvm/IR/Function.h'
    else:
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

    hasGC = Method(cast(Bool, bool))
    getGC = Method(cast(ConstCharPtr, str))
    setGC = Method(Void, cast(str, ConstCharPtr))


    getArgumentList = CustomMethod('Function_getArgumentList', PyObjectPtr)
    getBasicBlockList = CustomMethod('Function_getBasicBlockList', PyObjectPtr)
    getEntryBlock = Method(ref(BasicBlock))
    getValueSymbolTable = Method(ref(ValueSymbolTable))

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

    if LLVM_VERSION >= (3, 3):
        addFnAttr = Method(Void, Attribute.AttrKind)
        addAttributes = Method(Void, cast(int, Unsigned), ref(AttributeSet))
        removeAttributes = Method(Void, cast(int, Unsigned), ref(AttributeSet))
        #removeFnAttr = Method(Void, Attribute.AttrKind) # 3.4?
    else:
        addFnAttr = Method(Void, Attributes.AttrVal)
        removeFnAttr = Method(Void, ref(Attributes))
    #hasFnAttribute = Method(cast(Bool, bool), Attributes.AttrVal)

    Create = StaticMethod(ptr(Function),
                          ptr(FunctionType),
                          GlobalValue.LinkageTypes,
                          cast(str, ConstCharPtr),
                          ptr(Module)).require_only(2)

    eraseFromParent = Method()
    eraseFromParent.disowning = True

