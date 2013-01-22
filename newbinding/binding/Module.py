from binding import *
from namespace import llvm
from LLVMContext import LLVMContext
from StringRef import StringRef
from raw_ostream import raw_svector_ostream_helper
from AssemblyAnnotationWriter import AssemblyAnnotationWriter

Module = llvm.Class()
Module.include.add("llvm/Module.h")

new = Module.new(StringRef.From(str), LLVMContext.Ref)
delete = Module.delete()
getModuleIdentifier = Module.method(ConstStdString.To(str))
setModuleIdentifier = Module.method(Void, StringRef.From(str))
setDataLayout = Module.method(Void, StringRef.From(str))
setTargetTriple = Module.method(Void, StringRef.From(str))
setModuleInlineAsm = Module.method(Void, StringRef.From(str))
appendModuleInlineAsm = Module.method(Void, StringRef.From(str))
getContext = Module.method(LLVMContext.Ref)
dump = Module.method(Void)
print_ = Module.method(Void, raw_svector_ostream_helper.Ref,
                       AssemblyAnnotationWriter.Pointer)
print_.realname = 'print'
#getOrInsertFunction = Module.method(Constant, StringRef.From(str), FunctionType.Pointer)

