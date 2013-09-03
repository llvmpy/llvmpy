from binding import *
from ..namespace import llvm
from ..ADT.StringRef import StringRef

MemoryObject = llvm.Class()
if LLVM_VERSION >= (3, 4):
    StringRefMemoryObject = llvm.Class(MemoryObject)

@MemoryObject
class MemoryObject:
    _include_ = "llvm/Support/MemoryObject.h"

    getBase = Method(cast(Uint64, int))
    getExtent = Method(cast(Uint64, int))

    readBytes = CustomMethod('MemoryObject_readBytes',
                             PyObjectPtr,
                             cast(int, Uint64), #address
                             cast(int, Uint64)  #size 
                             )
    @CustomPythonMethod
    def readAll(self):
        result = self.readBytes(self.getBase(), self.getExtent())
        if not result:
            raise Exception("expected readBytes to be successful!")
        return result


if LLVM_VERSION >= (3, 4):
    @StringRefMemoryObject
    class StringRefMemoryObject:
        _include_ = "llvm/Support/StringRefMemoryObject.h"

        new = Constructor(cast(bytes, StringRef), cast(int, Uint64))
