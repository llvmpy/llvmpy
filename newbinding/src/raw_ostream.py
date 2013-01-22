from binding import *
from namespace import llvm
from LLVMContext import LLVMContext
from StringRef import StringRef

raw_ostream = llvm.Class()
raw_ostream.include.add("llvm/Support/raw_ostream.h")

raw_svector_ostream = raw_ostream.Subclass()
raw_svector_ostream.include.add("llvm/Support/raw_os_ostream.h")

# extra class to help binding
raw_svector_ostream_helper = raw_svector_ostream.Subclass()
create = raw_svector_ostream_helper.staticmethod(
                                            raw_svector_ostream_helper.Pointer)
delete = raw_svector_ostream_helper.delete()
str = raw_svector_ostream_helper.method(StringRef.To(str))
