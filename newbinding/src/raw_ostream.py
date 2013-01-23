from binding import *
from namespace import llvm
from LLVMContext import LLVMContext
from StringRef import StringRef

raw_ostream = llvm.Class()
raw_ostream.include.add("llvm/Support/raw_ostream.h")
delete = raw_ostream.delete()

raw_svector_ostream = raw_ostream.Subclass()
raw_svector_ostream.include.add("llvm/Support/raw_os_ostream.h")
str = raw_svector_ostream.method(StringRef.To(str))
