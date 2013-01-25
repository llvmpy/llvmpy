from binding import *
from namespace import llvm

@llvm.Class()
class LLVMContext:
    _include_ = "llvm/LLVMContext.h"

llvm.Function('getGlobalContext', ref(LLVMContext))
