from binding import *
from namespace import llvm
from Value import User

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

@Instruction
class Instruction:
    pass


@AtomicCmpXchgInst
class AtomicCmpXchgInst:
    pass

@AtomicRMWInst
class AtomicRMWInst:
    pass

@BinaryOperator
class BinaryOperator:
    pass

@CallInst
class CallInst:
    pass

@CmpInst
class CmpInst:
    pass

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
    pass

@SelectInst
class SelectInst:
    pass

@ShuffleVectorInst
class ShuffleVectorInst:
    pass

@StoreInst
class StoreInst:
    pass

@TerminatorInst
class TerminatorInst:
    pass

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

@ResumeInst
class ResumeInst:
    pass

@ReturnInst
class ReturnInst:
    pass

@SwitchInst
class SwitchInst:
    pass

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
    pass

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
