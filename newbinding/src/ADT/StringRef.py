from binding import *
from ..namespace import llvm

@llvm.Class()
class StringRef:
    _include_ = "llvm/ADT/StringRef.h"

