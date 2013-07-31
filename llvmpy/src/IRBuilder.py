from binding import *
from .namespace import llvm
from .LLVMContext import LLVMContext
from .BasicBlock import BasicBlock
from .Instruction import Instruction
from .Instruction import ReturnInst, CallInst, BranchInst, SwitchInst
from .Instruction import IndirectBrInst, InvokeInst, ResumeInst, PHINode
from .Instruction import UnreachableInst, AllocaInst, LoadInst, StoreInst
from .Instruction import FenceInst, AtomicCmpXchgInst, AtomicRMWInst, CmpInst
from .Instruction import LandingPadInst, VAArgInst
from .Instruction import AtomicOrdering, SynchronizationScope
from .ADT.SmallVector import SmallVector_Value, SmallVector_Unsigned
from .ADT.StringRef import StringRef
from .Value import Value, MDNode
from .Type import Type, IntegerType

IRBuilder = llvm.Class()

@IRBuilder
class IRBuilder:
    if LLVM_VERSION >= (3, 3):
        _include_ = 'llvm/IR/IRBuilder.h'
    else:
        _include_ = 'llvm/IRBuilder.h'

    _realname_ = 'IRBuilder<>'

    new = Constructor(ref(LLVMContext))
    delete = Destructor()

    GetInsertBlock = Method(ptr(BasicBlock))

    _SetInsertPoint_end_of_bb = Method(Void, ptr(BasicBlock))
    _SetInsertPoint_end_of_bb.realname = 'SetInsertPoint'
    _SetInsertPoint_before_instr = Method(Void, ptr(Instruction))
    _SetInsertPoint_before_instr.realname = 'SetInsertPoint'

    @CustomPythonMethod
    def SetInsertPoint(self, pt):
        if isinstance(pt, Instruction):
            return self._SetInsertPoint_before_instr(pt)
        elif isinstance(pt, BasicBlock):
            return self._SetInsertPoint_end_of_bb(pt)
        else:
            raise ValueError("Expected either an Instruction or a BasicBlock")

    isNamePreserving = Method(cast(Bool, bool))

    CreateRetVoid = Method(ptr(ReturnInst))
    CreateRet = Method(ptr(ReturnInst), ptr(Value))
    CreateAggregateRet = CustomMethod('IRBuilder_CreateAggregateRet',
                                      PyObjectPtr,      # ptr(ReturnInst),
                                      PyObjectPtr,      # list of Value
                                      cast(int, Unsigned))

    CreateBr = Method(ptr(BranchInst), ptr(BasicBlock))


    CreateCondBr = Method(ptr(BranchInst), ptr(Value), ptr(BasicBlock),
                          ptr(BasicBlock), ptr(MDNode)).require_only(3)

    CreateSwitch = Method(ptr(SwitchInst), ptr(Value), ptr(BasicBlock),
                          cast(int, Unsigned), ptr(MDNode)).require_only(2)

    CreateIndirectBr = Method(ptr(IndirectBrInst), ptr(Value),
                              cast(int, Unsigned)).require_only(1)

    _CreateInvoke = Method(ptr(InvokeInst), ptr(Value), ptr(BasicBlock),
                          ptr(BasicBlock), ref(SmallVector_Value),
                          cast(str, StringRef)).require_only(4)
    _CreateInvoke.realname = 'CreateInvoke'

    @CustomPythonMethod
    def CreateInvoke(self, *args):
        from llvmpy import extra
        args = list(args)
        valuelist = args[3]
        args[3] = extra.make_small_vector_from_values(*valuelist)
        return self._CreateInvoke(*args)

    CreateResume = Method(ptr(ResumeInst), ptr(Value))

    CreateUnreachable = Method(ptr(UnreachableInst))

    def _binop_has_nsw_nuw():
        sig = [ptr(Value), ptr(Value), ptr(Value), cast(str, StringRef),
               cast(bool, Bool), cast(bool, Bool)]
        op = Method(*sig).require_only(2)
        return op

    CreateAdd = _binop_has_nsw_nuw()
    CreateSub = _binop_has_nsw_nuw()
    CreateMul = _binop_has_nsw_nuw()
    CreateShl = _binop_has_nsw_nuw()

    def _binop_is_exact():
        sig = [ptr(Value), ptr(Value), ptr(Value), cast(str, StringRef),
               cast(bool, Bool)]
        op = Method(*sig).require_only(2)
        return op

    CreateUDiv = _binop_is_exact()
    CreateSDiv = _binop_is_exact()
    CreateLShr = _binop_is_exact()
    CreateAShr = _binop_is_exact()

    def _binop_basic():
        sig = [ptr(Value), ptr(Value), ptr(Value), cast(str, StringRef)]
        op = Method(*sig).require_only(2)
        return op

    CreateURem = _binop_basic()
    CreateSRem = _binop_basic()
    CreateAnd = _binop_basic()
    CreateOr = _binop_basic()
    CreateXor = _binop_basic()

    def _float_binop():
        sig = [ptr(Value), ptr(Value), ptr(Value), cast(str, StringRef),
               ptr(MDNode)]
        op = Method(*sig).require_only(2)
        return op

    CreateFAdd = _float_binop()
    CreateFSub = _float_binop()
    CreateFMul = _float_binop()
    CreateFDiv = _float_binop()
    CreateFRem = _float_binop()

    def _unop_has_nsw_nuw():
        sig = [ptr(Value), ptr(Value), cast(str, StringRef),
               cast(bool, Bool), cast(bool, Bool)]
        op = Method(*sig).require_only(1)
        return op

    CreateNeg = _unop_has_nsw_nuw()

    def _float_unop():
        sig = [ptr(Value), ptr(Value), cast(str, StringRef), ptr(MDNode)]
        op = Method(*sig).require_only(1)
        return op

    CreateFNeg = _float_unop()

    CreateNot = Method(ptr(Value),
                       ptr(Value), cast(str, StringRef)).require_only(1)


    CreateAlloca = Method(ptr(AllocaInst),
                          ptr(Type),            # ty
                          ptr(Value),           # arysize = 0
                          cast(str, StringRef), # name = ''
                          ).require_only(1)

    CreateLoad = Method(ptr(LoadInst),
                        ptr(Value), cast(str, StringRef)).require_only(1)

    CreateStore = Method(ptr(StoreInst), ptr(Value), ptr(Value),
                         cast(bool, Bool)).require_only(2)

    CreateAlignedLoad = Method(ptr(LoadInst), ptr(Value), cast(int, Unsigned),
                               cast(bool, Bool), cast(str, StringRef))
    CreateAlignedLoad.require_only(2)

    CreateAlignedStore = Method(ptr(StoreInst), ptr(Value), ptr(Value),
                                cast(int, Unsigned), cast(bool, Bool))
    CreateAlignedStore.require_only(3)

    CreateFence = Method(ptr(FenceInst),
                         AtomicOrdering, SynchronizationScope).require_only(1)

    CreateAtomicCmpXchg = Method(ptr(AtomicCmpXchgInst), ptr(Value), ptr(Value),
                                 ptr(Value), AtomicOrdering, SynchronizationScope)
    CreateAtomicCmpXchg.require_only(4)

    CreateAtomicRMW = Method(ptr(AtomicRMWInst), AtomicRMWInst.BinOp,
                             ptr(Value), ptr(Value), AtomicOrdering,
                             SynchronizationScope)
    CreateAtomicRMW.require_only(4)

    _CreateGEP = Method(ptr(Value), ptr(Value), ref(SmallVector_Value),
                       cast(str, StringRef))
    _CreateGEP.require_only(2)
    _CreateGEP.realname = 'CreateGEP'

    @CustomPythonMethod
    def CreateGEP(self, *args):
        from llvmpy import extra
        args = list(args)
        valuelist = args[1]
        args[1] = extra.make_small_vector_from_values(*valuelist)
        return self._CreateGEP(*args)

    _CreateInBoundsGEP = Method(ptr(Value), ptr(Value), ref(SmallVector_Value),
                        cast(str, StringRef))
    _CreateInBoundsGEP.require_only(2)
    _CreateInBoundsGEP.realname = 'CreateInBoundsGEP'

    @CustomPythonMethod
    def CreateInBoundsGEP(self, *args):
        from llvmpy import extra
        args = list(args)
        valuelist = args[1]
        args[1] = extra.make_small_vector_from_values(*valuelist)
        return self._CreateInBoundsGEP(*args)

    CreateStructGEP = Method(ptr(Value), ptr(Value), cast(int, Unsigned),
                             cast(str, StringRef)).require_only(2)

    CreateGlobalStringPtr = Method(ptr(Value), cast(str, StringRef),
                                   cast(str, StringRef)).require_only(1)

    def _value_type():
        sig = [ptr(Value), ptr(Value), ptr(Type), cast(str, StringRef)]
        op = Method(*sig).require_only(2)
        return op

    CreateTrunc = _value_type()
    CreateZExt = _value_type()
    CreateSExt = _value_type()
    CreateZExtOrTrunc = Method(ptr(Value), ptr(Value), ptr(IntegerType),
                               cast(str, StringRef)).require_only(2)
    CreateSExtOrTrunc = Method(ptr(Value), ptr(Value), ptr(IntegerType),
                               cast(str, StringRef)).require_only(2)
    CreateFPToUI = _value_type()
    CreateFPToSI = _value_type()
    CreateUIToFP = _value_type()
    CreateSIToFP = _value_type()
    CreateFPTrunc = _value_type()
    CreateFPExt = _value_type()
    CreatePtrToInt = _value_type()
    CreateIntToPtr = _value_type()
    CreateBitCast = _value_type()
    CreateZExtOrBitCast = _value_type()
    CreateSExtOrBitCast = _value_type()
    # Skip CreateCast
    CreateTruncOrBitCast = _value_type()
    CreateIntCast = Method(ptr(Value), ptr(Value), ptr(Type), cast(bool, Bool),
                           cast(str, StringRef)).require_only(3)
    CreateFPCast = _value_type()

    _CreateCall = Method(ptr(CallInst), ptr(Value), ref(SmallVector_Value),
                         cast(str, StringRef)).require_only(2)
    _CreateCall.realname = 'CreateCall'

    @CustomPythonMethod
    def CreateCall(self, *args):
        from llvmpy import extra
        args = list(args)
        valuelist = args[1]
        args[1] = extra.make_small_vector_from_values(*valuelist)
        return self._CreateCall(*args)

    # Skip specialized CreateICmp* and CreateFCmp*

    CreateICmp = Method(ptr(Value), CmpInst.Predicate, ptr(Value), ptr(Value),
                        cast(str, StringRef)).require_only(3)

    CreateFCmp = Method(ptr(Value), CmpInst.Predicate, ptr(Value), ptr(Value),
                        cast(str, StringRef)).require_only(3)

    CreatePHI = Method(ptr(PHINode), ptr(Type), cast(int, Unsigned),
                       cast(str, StringRef)).require_only(2)


    CreateSelect = Method(ptr(Value), ptr(Value), ptr(Value), ptr(Value),
                          cast(str, StringRef)).require_only(3)

    CreateVAArg = Method(ptr(VAArgInst), ptr(Value), ptr(Type),
                         cast(str, StringRef)).require_only(2)

    CreateExtractElement = _binop_basic()

    CreateInsertElement = Method(ptr(Value), ptr(Value), ptr(Value), ptr(Value),
                                 cast(str, StringRef)).require_only(3)

    CreateShuffleVector = Method(ptr(Value), ptr(Value), ptr(Value),
                                 ptr(Value), cast(str, StringRef))
    CreateShuffleVector.require_only(3)

    _CreateExtractValue = Method(ptr(Value), ptr(Value),
                                 ref(SmallVector_Unsigned),
                                 cast(str, StringRef))
    _CreateExtractValue.require_only(2)
    _CreateExtractValue.realname = 'CreateExtractValue'

    @CustomPythonMethod
    def CreateExtractValue(self, *args):
        from llvmpy import extra
        args = list(args)
        valuelist = args[1]
        args[1] = extra.make_small_vector_from_unsigned(*valuelist)
        return self._CreateExtractValue(*args)

    _CreateInsertValue = Method(ptr(Value),
                                ptr(Value), # Agg
                                ptr(Value), # Val
                                ref(SmallVector_Unsigned), # ArrayRef<unsigned>
                                cast(str, StringRef), # name
                                ).require_only(3)
    _CreateInsertValue.realname = 'CreateInsertValue'

    @CustomPythonMethod
    def CreateInsertValue(self, *args):
        from llvmpy import extra
        args = list(args)
        valuelist = args[2]
        args[2] = extra.make_small_vector_from_unsigned(*valuelist)
        return self._CreateInsertValue(*args)

    CreateLandingPad = Method(ptr(LandingPadInst), ptr(Type), ptr(Value),
                              cast(int, Unsigned), cast(str, StringRef))
    CreateLandingPad.require_only(3)

    CreateIsNull = Method(ptr(Value), ptr(Value), cast(str, StringRef))
    CreateIsNull.require_only(1)

    CreateIsNotNull = Method(ptr(Value), ptr(Value), cast(str, StringRef))
    CreateIsNotNull.require_only(1)

    CreatePtrDiff = _binop_basic()

    # New in llvm 3.3
    #CreateVectorSplat = Method(ptr(Value), cast(int, Unsigned), ptr(Value),
    #                           cast(str, StringRef))


    Insert = Method(ptr(Instruction),
                    ptr(Instruction),
                    cast(str, StringRef)).require_only(1)
