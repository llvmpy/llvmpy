from binding import *
from namespace import llvm
from LLVMContext import LLVMContext
from raw_ostream import raw_svector_ostream_helper

Type = llvm.Class()
Type.include.add('llvm/Type.h')

IntegerType = Type.Subclass()
CompositeType = Type.Subclass()
SequentialType = CompositeType.Subclass()
PointerType = SequentialType.Subclass()

getContext = Type.method(LLVMContext.Ref)
dump = Type.method(Void)
print_ = Type.method(Void, raw_svector_ostream_helper.Ref)
print_.realname = 'print'

def type_checker():
    return Type.method(Bool.To(bool))

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

isIntegerTy = Type.multimethod([Bool.To(bool)],
                               [Bool.To(bool), Unsigned.From(int)])


def type_factory():
    return Type.staticmethod(Type.Pointer, LLVMContext.Ref)

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

getIntNTy = Type.staticmethod(IntegerType.Pointer, LLVMContext.Ref, Unsigned.From(int))

def integer_factory():
    return Type.staticmethod(IntegerType.Pointer, LLVMContext.Ref)

getInt1Ty = integer_factory()
getInt8Ty = integer_factory()
getInt16Ty = integer_factory()
getInt32Ty = integer_factory()
getInt64Ty = integer_factory()

def pointer_factory():
    return Type.staticmethod(PointerType.Pointer, LLVMContext.Ref)

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
getIntNPtrTy = Type.staticmethod(PointerType.Pointer,
                                 LLVMContext.Ref, Unsigned.From(int))


