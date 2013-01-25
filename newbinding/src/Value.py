from binding import *
from namespace import llvm
from raw_ostream import raw_ostream
from AssemblyAnnotationWriter import AssemblyAnnotationWriter
from Type import Type
from LLVMContext import LLVMContext
from StringRef import StringRef

Value = llvm.Class()

@Value
class Value:

    dump = Method()

    print_ = Method(Void, ref(raw_ostream), ptr(AssemblyAnnotationWriter))
    print_.realname = 'print'

    getType = Method(ptr(Type))
    getContext = Method(ref(LLVMContext))

    hasName = Method(cast(Bool, bool))
    # skip getValueName, setValueName
    getName = Method(cast(StringRef, str))
    setName = Method(Void, cast(str, StringRef))

    replaceAllUsesWith = Method(Void, ptr(Value))
