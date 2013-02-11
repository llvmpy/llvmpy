from binding import *
from namespace import llvm
from Value import Value, MDNode, User, BasicBlock, Function
from ADT.StringRef import StringRef
from CallingConv import CallingConv
from Attributes import Attributes
from Constant import ConstantInt
from Type import Type


Instruction = llvm.Class(User)
AtomicCmpXchgInst = llvm.Class(Instruction)
AtomicRMWInst = llvm.Class(Instruction)
BinaryOperator = llvm.Class(Instruction)
CallInst = llvm.Class(Instruction)
CmpInst = llvm.Class(Instruction)
ExtractElementInst = llvm.Class(Instruction)
FenceInst = llvm.Class(Instruction)
GetElementPtrInst = llvm.Class(Instruction)
InsertElementInst = llvm.Class(Instruction)
InsertValueInst = llvm.Class(Instruction)
LandingPadInst = llvm.Class(Instruction)
PHINode = llvm.Class(Instruction)
SelectInst = llvm.Class(Instruction)
ShuffleVectorInst = llvm.Class(Instruction)
StoreInst = llvm.Class(Instruction)
TerminatorInst = llvm.Class(Instruction)
UnaryInstruction = llvm.Class(Instruction)

IntrinsicInst = llvm.Class(CallInst)

FCmpInst = llvm.Class(CmpInst)
ICmpInst = llvm.Class(CmpInst)

BranchInst = llvm.Class(TerminatorInst)
IndirectBrInst = llvm.Class(TerminatorInst)
InvokeInst = llvm.Class(TerminatorInst)
ResumeInst = llvm.Class(TerminatorInst)
ReturnInst = llvm.Class(TerminatorInst)
SwitchInst = llvm.Class(TerminatorInst)
UnreachableInst = llvm.Class(TerminatorInst)

AllocaInst = llvm.Class(UnaryInstruction)
CastInst = llvm.Class(UnaryInstruction)
ExtractValueInst = llvm.Class(UnaryInstruction)
LoadInst = llvm.Class(UnaryInstruction)
VAArgInst = llvm.Class(UnaryInstruction)

DbgInfoIntrinsic = llvm.Class(IntrinsicInst)
MemIntrinsic = llvm.Class(IntrinsicInst)
VACopyInst = llvm.Class(IntrinsicInst)
VAEndInst = llvm.Class(IntrinsicInst)
VAStartInst = llvm.Class(IntrinsicInst)

BitCastInst = llvm.Class(CastInst)
FPExtInst = llvm.Class(CastInst)
FPToSIInst = llvm.Class(CastInst)
FPToUIInst = llvm.Class(CastInst)
FPTruncInst = llvm.Class(CastInst)

AtomicOrdering = llvm.Enum('AtomicOrdering',
                           'NotAtomic', 'Unordered', 'Monotonic', 'Acquire',
                           'Release', 'AcquireRelease',
                           'SequentiallyConsistent')

SynchronizationScope = llvm.Enum('SynchronizationScope',
                                 'SingleThread', 'CrossThread')




@Instruction
class Instruction:
    removeFromParent = Method()
    eraseFromParent = Method()
    eraseFromParent.disowning = True

    getParent = Method(ptr(BasicBlock))
    getOpcode = Method(cast(Unsigned, int))
    getOpcodeName = Method(cast(ConstCharPtr, str))

    insertBefore = Method(Void, ptr(Instruction))
    insertAfter = Method(Void, ptr(Instruction))
    moveBefore = Method(Void, ptr(Instruction))
    
    isTerminator = Method(cast(Bool, bool))
    isBinaryOp = Method(cast(Bool, bool))
    isShift = Method(cast(Bool, bool))
    isCast = Method(cast(Bool, bool))
    isLogicalShift = Method(cast(Bool, bool))
    isArithmeticShift = Method(cast(Bool, bool))
    hasMetadata = Method(cast(Bool, bool))
    hasMetadataOtherThanDebugLoc = Method(cast(Bool, bool))
    isAssociative = Method(cast(Bool, bool))
    isCommutative = Method(cast(Bool, bool))
    isIdempotent = Method(cast(Bool, bool))
    isNilpotent = Method(cast(Bool, bool))
    mayWriteToMemory = Method(cast(Bool, bool))
    mayReadFromMemory = Method(cast(Bool, bool))
    mayReadOrWriteMemory = Method(cast(Bool, bool))
    mayThrow = Method(cast(Bool, bool))
    mayHaveSideEffects = Method(cast(Bool, bool))

    hasMetadata = Method(cast(Bool, bool))
    getMetadata = Method(ptr(MDNode), cast(str, StringRef))
    setMetadata = Method(Void, cast(str, StringRef), ptr(MDNode))

    clone = Method(ptr(Instruction))

# LLVM 3.3
#    hasUnsafeAlgebra = Method(cast(Bool, bool))
#    hasNoNans = Method(cast(Bool, bool))
#    hasNoInfs = Method(cast(Bool, bool))
#    hasNoSignedZeros = Method(cast(Bool, bool))
#    hasAllowReciprocal = Method(cast(Bool, bool))


@AtomicCmpXchgInst
class AtomicCmpXchgInst:
    pass

@AtomicRMWInst
class AtomicRMWInst:
    BinOp = Enum('Xchg', 'Add', 'Sub', 'And', 'Nand', 'Or', 'Xor', 'Max', 'Min',
                 'UMax', 'UMin', 'FIRST_BINOP', 'LAST_BINOP', 'BAD_BINOP')

@BinaryOperator
class BinaryOperator:
    pass

@CallInst
class CallInst:
    _downcast_ = Value, Instruction
    getCallingConv = Method(CallingConv.ID)
    setCallingConv = Method(Void, CallingConv.ID)
    getParamAlignment = Method(cast(Unsigned, int), cast(int, Unsigned))
    addAttribute = Method(Void, cast(int, Unsigned), ref(Attributes))
    removeAttribute = Method(Void, cast(int, Unsigned), ref(Attributes))
    getCalledFunction = Method(ptr(Function))
    getCalledValue = Method(ptr(Value))
    setCalledFunction = Method(Void, ptr(Function))
    isInlineAsm = Method(cast(Bool, bool))

    CreateMalloc = StaticMethod(ptr(Instruction),
                                ptr(BasicBlock),    # insertAtEnd
                                ptr(Type),          # intptrty
                                ptr(Type),          # allocty
                                ptr(Value),         # allocsz
                                ptr(Value),         # array size = 0
                                ptr(Function),      # malloc fn = 0
                                cast(str, StringRef), # name
                                ).require_only(4)

    CreateFree = StaticMethod(ptr(Instruction), ptr(Value), ptr(BasicBlock))

@CmpInst
class CmpInst:
    Predicate = Enum('FCMP_FALSE', 'FCMP_OEQ', 'FCMP_OGT', 'FCMP_OGE',
                     'FCMP_OLT', 'FCMP_OLE', 'FCMP_ONE', 'FCMP_ORD', 'FCMP_UNO',
                     'FCMP_UEQ', 'FCMP_UGT', 'FCMP_UGE', 'FCMP_ULT', 'FCMP_ULE',
                     'FCMP_UNE', 'FCMP_TRUE', 'FIRST_FCMP_PREDICATE',
                     'LAST_FCMP_PREDICATE',
                     'BAD_FCMP_PREDICATE',
                     'ICMP_EQ', 'ICMP_NE', 'ICMP_UGT', 'ICMP_UGE', 'ICMP_ULT',
                     'ICMP_ULE', 'ICMP_SGT', 'ICMP_SGE', 'ICMP_SLT', 'ICMP_SLE',
                     'FIRST_ICMP_PREDICATE',
                     'LAST_ICMP_PREDICATE',
                     'BAD_ICMP_PREDICATE',)

    getPredicate = Method(Predicate)

@ExtractElementInst
class ExtractElementInst:
    pass

@FenceInst
class FenceInst:
    pass

@GetElementPtrInst
class GetElementPtrInst:
    pass

@InsertElementInst
class InsertElementInst:
    pass

@InsertValueInst
class InsertValueInst:
    pass

@LandingPadInst
class LandingPadInst:
    pass

@PHINode
class PHINode:
    getNumIncomingValues = Method(cast(Unsigned, int))
    getIncomingValue = Method(ptr(Value), cast(int, Unsigned))
    setIncomingValue = Method(Void, cast(int, Unsigned), ptr(Value))
    getIncomingBlock = Method(ptr(BasicBlock), cast(int, Unsigned))
    setIncomingBlock = Method(Void, cast(int, Unsigned), ptr(BasicBlock))
    addIncoming = Method(Void, ptr(Value), ptr(BasicBlock))
    hasConstantValue = Method(ptr(Value))
    getBasicBlockIndex = Method(cast(Int, int), ptr(BasicBlock))

@SelectInst
class SelectInst:
    pass

@ShuffleVectorInst
class ShuffleVectorInst:
    pass

@StoreInst
class StoreInst:
    _downcast_ = Instruction
    isVolatile = Method(cast(Bool, bool))
    isSimple = Method(cast(Bool, bool))
    isUnordered = Method(cast(Bool, bool))
    isAtomic = Method(cast(Bool, bool))

    setVolatile = Method(Void, cast(Bool, bool))

    getAlignment = Method(cast(Unsigned, int))
    setAlignment = Method(Void, cast(int, Unsigned))

    setAtomic = Method(Void,
                       AtomicOrdering,
                       SynchronizationScope).require_only(1)

    classof = StaticMethod(cast(Bool, bool), ptr(Value))

@TerminatorInst
class TerminatorInst:
    getNumSuccessors = Method(cast(Unsigned, int))
    getSuccessor = Method(ptr(BasicBlock), cast(int, Unsigned))
    setSuccessor = Method(Void, cast(int, Unsigned), ptr(BasicBlock))

@UnaryInstruction
class UnaryInstruction:
    pass

#call

@IntrinsicInst
class IntrinsicInst:
    pass

#compare

@FCmpInst
class FCmpInst:
    pass

@ICmpInst
class ICmpInst:
    pass

# terminator
@BranchInst
class BranchInst:
    pass

@IndirectBrInst
class IndirectBrInst:
    pass

@InvokeInst
class InvokeInst:
    _downcast_ = Value, Instruction
    getCallingConv = Method(CallingConv.ID)
    setCallingConv = Method(Void, CallingConv.ID)
    getParamAlignment = Method(cast(Unsigned, int), cast(int, Unsigned))
    addAttribute = Method(Void, cast(int, Unsigned), ref(Attributes))
    removeAttribute = Method(Void, cast(int, Unsigned), ref(Attributes))
    getCalledFunction = Method(ptr(Function))
    getCalledValue = Method(ptr(Value))
    setCalledFunction = Method(Void, ptr(Function))

@ResumeInst
class ResumeInst:
    pass

@ReturnInst
class ReturnInst:
    pass

@SwitchInst
class SwitchInst:
    getCondition = Method(ptr(Value))
    setCondition = Method(Void, ptr(Value))
    getDefaultDest = Method(ptr(BasicBlock))
    setDefaultDest = Method(Void, ptr(BasicBlock))
    getNumCases = Method(cast(int, Unsigned))
    addCase = Method(Void, ptr(ConstantInt), ptr(BasicBlock))


@UnreachableInst
class UnreachableInst:
    pass

# unary
@AllocaInst
class AllocaInst:
    pass

@CastInst
class CastInst:
    pass

@ExtractValueInst
class ExtractValueInst:
    pass

@LoadInst
class LoadInst:
    _downcast_ = Value, Instruction
    isVolatile = Method(cast(Bool, bool))
    isSimple = Method(cast(Bool, bool))
    isUnordered = Method(cast(Bool, bool))
    isAtomic = Method(cast(Bool, bool))

    setVolatile = Method(Void, cast(Bool, bool))

    getAlignment = Method(cast(Unsigned, int))
    setAlignment = Method(Void, cast(int, Unsigned))

    setAtomic = Method(Void,
                       AtomicOrdering,
                       SynchronizationScope).require_only(1)

    classof = StaticMethod(cast(Bool, bool), ptr(Value))

@VAArgInst
class VAArgInst:
    pass

# intrinsic
@DbgInfoIntrinsic
class DbgInfoIntrinsic:
    pass

@MemIntrinsic
class MemIntrinsic:
    pass

@VACopyInst
class VACopyInst:
    pass

@VAEndInst
class VAEndInst:
    pass

@VAStartInst
class VAStartInst:
    pass

@BitCastInst
class BitCastInst:
    pass

@FPExtInst
class FPExtInst:
    pass

@FPToSIInst
class FPToSIInst:
    pass

@FPToUIInst
class FPToUIInst:
    pass

@FPTruncInst
class FPTruncInst:
    pass

