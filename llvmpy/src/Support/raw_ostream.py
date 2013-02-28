from binding import *
from ..namespace import llvm
from ..LLVMContext import LLVMContext
from ..ADT.StringRef import StringRef

@llvm.Class()
class raw_ostream:
    _include_ = "llvm/Support/raw_ostream.h"
    delete = Destructor()
    flush = Method()

@llvm.Class(raw_ostream)
class raw_svector_ostream:
    _include_ = "llvm/Support/raw_os_ostream.h"
    _base_ = raw_ostream

    str = Method(cast(str, StringRef))
    bytes = Method(cast(bytes, StringRef))
    bytes.realname = 'str'

