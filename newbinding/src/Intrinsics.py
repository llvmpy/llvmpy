from binding import *
from namespace import llvm

from Module import Module
from Function import Function


Intrinsic = llvm.Class() # fake class (actually a namespace)

@Intrinsic
class Intrinsic:
    getDeclaration = CustomStaticMethod('Intrinsic_getDeclaration',
                                        PyObjectPtr,          # Function*
                                        ptr(Module),
                                        cast(int, Unsigned),  # intrinsic id
                                        PyObjectPtr,          # list of Type
                                        ).require_only(2)
