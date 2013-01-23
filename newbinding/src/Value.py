from binding import *
from namespace import llvm
from raw_ostream import raw_ostream
from AssemblyAnnotationWriter import AssemblyAnnotationWriter

Value = llvm.Class()
print_ = Value.method(Void, raw_ostream.Ref, AssemblyAnnotationWriter.Pointer)
print_.realname = 'print'
