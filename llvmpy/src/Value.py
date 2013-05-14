from binding import *
from .namespace import llvm

# forward declarations
Value = llvm.Class()
Argument = llvm.Class(Value)
MDNode = llvm.Class(Value)
MDString = llvm.Class(Value)
User = llvm.Class(Value)
BasicBlock = llvm.Class(Value)
ValueSymbolTable = llvm.Class()
Constant = llvm.Class(User)
GlobalValue = llvm.Class(Constant)
Function = llvm.Class(GlobalValue)
UndefValue = llvm.Class(Constant)
ConstantInt = llvm.Class(Constant)
ConstantFP = llvm.Class(Constant)
ConstantArray = llvm.Class(Constant)
ConstantStruct = llvm.Class(Constant)
ConstantVector = llvm.Class(Constant)
ConstantDataSequential = llvm.Class(Constant)
ConstantDataArray = llvm.Class(ConstantDataSequential)
ConstantExpr = llvm.Class(Constant)

from .Support.raw_ostream import raw_ostream
from .Assembly.AssemblyAnnotationWriter import AssemblyAnnotationWriter
from .Type import Type
from .LLVMContext import LLVMContext
from .ADT.StringRef import StringRef


@Value
class Value:

    ValueTy = Enum('''
        ArgumentVal, BasicBlockVal, FunctionVal, GlobalAliasVal,
        GlobalVariableVal, UndefValueVal, BlockAddressVal, ConstantExprVal,
        ConstantAggregateZeroVal, ConstantDataArrayVal, ConstantDataVectorVal,
        ConstantIntVal, ConstantFPVal, ConstantArrayVal, ConstantStructVal,
        ConstantVectorVal, ConstantPointerNullVal, MDNodeVal, MDStringVal,
        InlineAsmVal, PseudoSourceValueVal, FixedStackPseudoSourceValueVal,
        InstructionVal, ConstantFirstVal, ConstantLastVal
        ''')

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
    getNumUses = Method(cast(Unsigned, int))

    @CustomPythonMethod
    def __str__(self):
        from llvmpy import extra
        os = extra.make_raw_ostream_for_printing()
        self.print_(os, None)
        return os.str()

    getValueID = Method(cast(Unsigned, int))

    mutateType = Method(Void, ptr(Type))
