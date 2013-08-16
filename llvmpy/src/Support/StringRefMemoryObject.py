from binding import *
from ..namespace import llvm
from ..ADT.StringRef import StringRef

MemoryObject = llvm.Class()
if LLVM_VERSION >= (3, 4):
    StringRefMemoryObject = llvm.Class(MemoryObject)

@MemoryObject
class MemoryObject:
    pass

if LLVM_VERSION >= (3, 4):
    @StringRefMemoryObject
    class StringRefMemoryObject:
        _include_ = "llvm/Support/StringRefMemoryObject.h"

        new = Constructor(cast(bytes, StringRef), cast(int, Uint64))

        getBase = Method(cast(Uint64, int))
        getExtent = Method(cast(Uint64, int))
