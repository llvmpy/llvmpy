from binding import *
from namespace import llvm
from raw_ostream import raw_ostream
from AssemblyAnnotationWriter import AssemblyAnnotationWriter
from Type import Type
from LLVMContext import LLVMContext
from StringRef import StringRef

Value = llvm.Class()
# forward declarations
User = llvm.Class(Value)
BasicBlock = llvm.Class(Value)
Constant = llvm.Class(User)
GlobalValue = llvm.Class(Constant)
Function = llvm.Class(GlobalValue)

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

    list_use = CustomMethod('Value_use_iterator_to_list', PyObjectPtr)

    hasOneUse = Method(cast(Bool, bool))
    hasNUses = Method(cast(Bool, bool), cast(int, Unsigned))
    isUsedInBasicBlock = Method(cast(Bool, bool), BasicBlock)

    @CustomPythonMethod
    def __str__(self):
        import extra
        os = extra.make_raw_ostream_for_printing()
        self.print_(os, None)
        return os.str()
