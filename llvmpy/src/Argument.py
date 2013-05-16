from binding import *
from .namespace import llvm
from .Value import Argument, Value
from .Attributes import Attributes

@Argument
class Argument:
    _include_ = 'llvm/Argument.h'

    _downcast_ = Value

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
