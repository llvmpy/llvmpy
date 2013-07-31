from binding import *
from .namespace import llvm

@llvm.Class()
class LLVMContext:
    if LLVM_VERSION >= (3, 3):
        _include_ = "llvm/IR/LLVMContext.h"
    else:
        _include_ = "llvm/LLVMContext.h"

llvm.Function('getGlobalContext', ref(LLVMContext))
