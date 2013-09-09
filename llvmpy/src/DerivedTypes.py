from binding import *
from .namespace import llvm
from .LLVMContext import LLVMContext
from .Type import Type
from .ADT.SmallVector import SmallVector_Type

FunctionType = llvm.Class(Type)

@FunctionType
class FunctionType:
    if LLVM_VERSION >= (3, 3):
        _include_ = 'llvm/IR/DerivedTypes.h'
    else:
        _include_ = 'llvm/DerivedTypes.h'
    _downcast_ = Type

    _get = StaticMethod(ptr(FunctionType), ptr(Type), cast(bool, Bool))
    _get |= StaticMethod(ptr(FunctionType), ptr(Type), ref(SmallVector_Type),
                         cast(bool, Bool))
    _get.realname = 'get'

    @CustomPythonStaticMethod
    def get(*args):
        from llvmpy import extra
        if len(args) == 3:
            typelist = args[1]
            sv = extra.make_small_vector_from_types(*typelist)
            return FunctionType._get(args[0], sv, args[2])
        else:
            return FunctionType._get(*args)

    isVarArg = Method(cast(Bool, bool))
    getReturnType = Method(ptr(Type))
    getParamType = Method(ptr(Type), cast(int, Unsigned))
    getNumParams = Method(cast(Unsigned, int))

