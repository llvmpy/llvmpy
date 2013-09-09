from binding import *
from .namespace import llvm
from .Value import Argument, Value
if LLVM_VERSION >= (3, 3):
    from .Attributes import AttributeSet, Attribute
else:
    from .Attributes import Attributes

@Argument
class Argument:
    if LLVM_VERSION >= (3, 3):
        _include_ = 'llvm/IR/Argument.h'
    else:
        _include_ = 'llvm/Argument.h'

    _downcast_ = Value

    if LLVM_VERSION >= (3, 3):
        addAttr = Method(Void, ref(AttributeSet))
        removeAttr = Method(Void, ref(AttributeSet))
    else:
        addAttr = Method(Void, ref(Attributes))
        removeAttr = Method(Void, ref(Attributes))

    getParamAlignment = Method(cast(Unsigned, int))

    getArgNo = Method(cast(Unsigned, int))

    hasByValAttr = Method(cast(Bool, bool))
    hasNestAttr = Method(cast(Bool, bool))
    hasNoAliasAttr = Method(cast(Bool, bool))
    hasNoCaptureAttr = Method(cast(Bool, bool))
    hasStructRetAttr = Method(cast(Bool, bool))

    if LLVM_VERSION > (3, 2):
        hasReturnedAttr = Method(cast(Bool, bool))
