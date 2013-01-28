from binding import *
from namespace import llvm
from Value import GlobalValue, Constant, Function, Argument
from Type import Type
from DerivedTypes import FunctionType
from LLVMContext import LLVMContext

@Function
class Function:
    _include_ = 'llvm/Function.h'
    _downcast_  = GlobalValue, Constant

    getReturnType = Method(ptr(Type))
    getFunctionType = Method(ptr(FunctionType))
    getContext = Method(ref(LLVMContext))
    isVarArg = Method(cast(Bool, bool))
    getIntrinsicID = Method(cast(Unsigned, int))
    isIntrinsic = Method(cast(Bool, bool))

    getArgumentList = CustomMethod('Function_getArgumentList', PyObjectPtr)
    getBasicBlockList = CustomMethod('Function_getBasicBlockList', PyObjectPtr)
