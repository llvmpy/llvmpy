from binding import *
from namespace import llvm

StringRef = llvm.Class()
StringRef.include.add("llvm/ADT/StringRef.h")

