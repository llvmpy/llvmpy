from binding import *
from namespace import llvm
from LLVMContext import LLVMContext
from Type import Type
from SmallVector import SmallVector_Type

FunctionType = llvm.Class(Type)

@FunctionType
class FunctionType:
    _include_ = 'llvm/DerivedTypes.h'
    get = StaticMethod(ptr(FunctionType), ptr(Type), cast(bool, Bool))
    get |= StaticMethod(ptr(FunctionType), ptr(Type), ref(SmallVector_Type), cast(bool, Bool))
    isVarArg = Method(cast(Bool, bool))
    getReturnType = Method(ptr(Type))
    getParamType = Method(ptr(Type), cast(int, Unsigned))
    getNumParams = Method(cast(Unsigned, int))

