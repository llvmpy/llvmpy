from binding import *
from namespace import llvm
from LLVMContext import LLVMContext
from Type import Type
from SmallVector import SmallVector_Type

FunctionType = Type.Subclass()
FunctionType.include.add('llvm/DerivedTypes.h')

_get_signatures = [(FunctionType.Pointer,
                    Type.Pointer, Bool.From(bool)),
                   (FunctionType.Pointer,
                    Type.Pointer, SmallVector_Type.Ref, Bool.From(bool))]

get = FunctionType.staticmultimethod(*_get_signatures)

isVarArg = FunctionType.method(Bool.To(bool))
getReturnType = FunctionType.method(Type.Pointer)
getParamType = FunctionType.method(Type.Pointer, Unsigned.From(int))
getNumParams = FunctionType.method(Unsigned.To(int))
