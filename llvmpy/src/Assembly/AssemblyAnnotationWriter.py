from binding import *
from ..namespace import llvm

@llvm.Class()
class AssemblyAnnotationWriter:
    _include_ = "llvm/Assembly/AssemblyAnnotationWriter.h"

