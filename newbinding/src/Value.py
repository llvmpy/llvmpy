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

    list_use = IterToList(ptr(User), (), 'llvm::Value::use_iterator',
                          'use_begin', 'use_end')

    hasOneUse = Method(cast(Bool, bool))
    hasNUses = Method(cast(Bool, bool), cast(int, Unsigned))
    isUsedInBasicBlock = Method(cast(Bool, bool), BasicBlock)
