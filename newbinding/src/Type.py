from binding import *
from namespace import llvm
from LLVMContext import LLVMContext
from raw_ostream import raw_ostream

Type = llvm.Class()
IntegerType = llvm.Class(Type)
CompositeType = llvm.Class(Type)
SequentialType = llvm.Class(CompositeType)
PointerType = llvm.Class(SequentialType)

@Type
class Type:
    _include_ = 'llvm/Type.h'

    getContext = Method(ref(LLVMContext))
    dump = Method()
    print_ = Method(Void, ref(raw_ostream))
    print_.realname = 'print'

    def type_checker():
        return Method(cast(Bool, bool))

    isVoidTy = type_checker()
    isHalfTy = type_checker()
    isFloatTy = type_checker()
    isDoubleTy = type_checker()
    isX86_FP80Ty = type_checker()
    isFP128Ty = type_checker()
    isPPC_FP128Ty = type_checker()
    isFloatingPointTy = type_checker()
    isX86_MMXTy = type_checker()
    isFPOrFPVectorTy = type_checker()
    isLabelTy = type_checker()
    isMetadataTy = type_checker()
    isIntOrIntVectorTy = type_checker()
    isFunctionTy = type_checker()
    isStructTy = type_checker()
    isArrayTy = type_checker()
    isPointerTy = type_checker()
    isPtrOrPtrVectorTy = type_checker()
    isVectorTy = type_checker()
    isEmptyTy = type_checker()
    isPrimitiveType = type_checker()
    isDerivedType = type_checker()
    isFirstClassType = type_checker()
    isSingleValueType = type_checker()
    isAggregateType = type_checker()
    isSized = type_checker()

    isIntegerTy = Method(cast(Bool, bool))
    isIntegerTy |= Method(cast(Bool, bool), cast(int, Unsigned))


    def type_factory():
        return StaticMethod(ptr(Type), ref(LLVMContext))

    getVoidTy = type_factory()
    getLabelTy = type_factory()
    getHalfTy = type_factory()
    getFloatTy = type_factory()
    getDoubleTy = type_factory()
    getMetadataTy = type_factory()
    getX86_FP80Ty = type_factory()
    getFP128Ty = type_factory()
    getPPC_FP128Ty = type_factory()
    getX86_MMXTy = type_factory()

    getIntNTy = StaticMethod(ptr(IntegerType), ref(LLVMContext), cast(Unsigned, int))

    def integer_factory():
        return StaticMethod(ptr(IntegerType), ref(LLVMContext))

    getInt1Ty = integer_factory()
    getInt8Ty = integer_factory()
    getInt16Ty = integer_factory()
    getInt32Ty = integer_factory()
    getInt64Ty = integer_factory()

    def pointer_factory():
        return StaticMethod(ptr(PointerType), ref(LLVMContext))

    getHalfPtrTy = pointer_factory()
    getFloatPtrTy = pointer_factory()
    getDoublePtrTy = pointer_factory()
    getX86_FP80PtrTy = pointer_factory()
    getFP128PtrTy = pointer_factory()
    getPPC_FP128PtrTy = pointer_factory()
    getX86_MMXPtrTy = pointer_factory()
    getInt1PtrTy = pointer_factory()
    getInt8PtrTy = pointer_factory()
    getInt16PtrTy = pointer_factory()
    getInt32PtrTy = pointer_factory()
    getInt64PtrTy = pointer_factory()
    getIntNPtrTy = StaticMethod(ptr(PointerType),
                                ref(LLVMContext), cast(int, Unsigned))


@IntegerType
class IntegerType:
    pass


@CompositeType
class CompositeType:
    pass

@SequentialType
class SequentialType:
    pass

@PointerType
class PointerType:
    pass

