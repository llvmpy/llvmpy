from binding import *
from namespace import llvm
from LLVMContext import LLVMContext
from Type import Type

FunctionType = Type.Subclass()
FunctionType.include.add('llvm/DerivedTypes.h')

get = FunctionType.staticmethod(FunctionType.Pointer, Type.Pointer, Bool.From(bool))
isVarArg = FunctionType.method(Bool.To(bool))
getReturnType = FunctionType.method(Type.Pointer)
getParamType = FunctionType.method(Type.Pointer, Unsigned.From(int))
getNumParams = FunctionType.method(Unsigned.To(int))
