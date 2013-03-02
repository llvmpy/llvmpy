from binding import *
from .namespace import llvm
from src.ADT.StringRef import StringRef

PassRegistry = llvm.Class()

from src.PassSupport import PassInfo

@PassRegistry
class PassRegistry:
    _include_ = 'llvm/PassRegistry.h'

    delete = Destructor()

    getPassRegistry = StaticMethod(ownedptr(PassRegistry))

    getPassInfo = Method(const(ptr(PassInfo)), cast(str, StringRef))

    # This is a custom method that wraps enumerateWith
    # Returns list of tuples of (pass-arg, pass-name)
    enumerate = CustomMethod('PassRegistry_enumerate', PyObjectPtr)
