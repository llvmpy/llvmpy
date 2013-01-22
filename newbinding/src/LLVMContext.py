from binding import *
from namespace import llvm

LLVMContext = llvm.Class()
LLVMContext.include.add("llvm/LLVMContext.h")

getGlobalContext = llvm.Function(LLVMContext.Ref)

