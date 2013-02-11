from binding import *
from namespace import llvm
from Value import Argument
from Attributes import Attributes

@Argument
class Argument:
    _include_ = 'llvm/Argument.h'

    addAttr = Method(Void, ref(Attributes))
    removeAttr = Method(Void, ref(Attributes))
    getParamAlignment = Method(cast(Unsigned, int))
    
