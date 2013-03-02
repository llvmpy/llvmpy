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

