from binding import *
from namespace import llvm
from raw_ostream import raw_ostream
from AssemblyAnnotationWriter import AssemblyAnnotationWriter
from Type import Type
from LLVMContext import LLVMContext
from StringRef import StringRef
#
Value = llvm.Class()

dump = Value.method(Void)

print_ = Value.method(Void, raw_ostream.Ref, AssemblyAnnotationWriter.Pointer)
print_.realname = 'print'

getType = Value.method(Type.Pointer)
getContext = Value.method(LLVMContext.Ref)

hasName = Value.method(Bool.To(bool))
# skip getValueName, setValueName
getName = Value.method(StringRef.To(str))
setName = Value.method(Void, StringRef.From(str))

replaceAllUsesWith = Value.method(Void, Value.Pointer)