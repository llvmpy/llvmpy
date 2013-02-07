from binding import *
from namespace import llvm
from Value import MDNode
from ADT.StringRef import StringRef
from Module import Module
from Support.raw_ostream import raw_ostream
from Assembly.AssemblyAnnotationWriter import AssemblyAnnotationWriter

@MDNode
class MDNode:
    pass

@llvm.Class()
class NamedMDNode:
    eraseFromParent = Method()
    dropAllReferences = Method()
    getParent = Method(ptr(Module))
    getOperand = Method(ptr(MDNode), cast(int, Unsigned))
    getNumOperands = Method(cast(Unsigned, int))
    getName = Method(cast(StringRef, str))
    print_ = Method(Void, ref(raw_ostream), ptr(AssemblyAnnotationWriter))
    print_.realname = "print"
    dump = Method()

