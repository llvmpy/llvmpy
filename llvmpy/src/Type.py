from binding import *
from .namespace import llvm
from .LLVMContext import LLVMContext
from .Support.raw_ostream import raw_ostream
from .ADT.StringRef import StringRef

Type = llvm.Class()
IntegerType = llvm.Class(Type)
CompositeType = llvm.Class(Type)
StructType = llvm.Class(CompositeType)
SequentialType = llvm.Class(CompositeType)
ArrayType = llvm.Class(SequentialType)
PointerType = llvm.Class(SequentialType)
VectorType = llvm.Class(SequentialType)

@Type
class Type:
    if LLVM_VERSION >= (3, 3):
        _include_ = 'llvm/IR/Type.h'
    else:
        _include_ = 'llvm/Type.h'

    TypeID = Enum('''
        VoidTyID, HalfTyID, FloatTyID, DoubleTyID,
        X86_FP80TyID, FP128TyID, PPC_FP128TyID, LabelTyID,
        MetadataTyID, X86_MMXTyID, IntegerTyID, FunctionTyID,
        StructTyID, ArrayTyID, PointerTyID, VectorTyID,
        NumTypeIDs, LastPrimitiveTyID, FirstDerivedTyID
        ''')

    getContext = Method(ref(LLVMContext))
    dump = Method()
    print_ = Method(Void, ref(raw_ostream))
    print_.realname = 'print'

    getTypeID = Method(TypeID)

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

    getIntegerBitWidth = Method(cast(Unsigned, int))
    getFunctionParamType = Method(ptr(Type), cast(int, Unsigned))
    getFunctionNumParams = Method(cast(int, Unsigned))

    isFunctionVarArg = type_checker()

    getStructName = Method(cast(StringRef, str))
    getStructNumElements = Method(cast(Unsigned, int))
    getStructElementType = Method(ptr(Type), cast(int, Unsigned))
    getSequentialElementType = Method(ptr(Type))

    # Factories


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

    getIntNTy = StaticMethod(ptr(IntegerType),
                             ref(LLVMContext), cast(Unsigned, int))

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

    @CustomPythonMethod
    def __str__(self):
        from llvmpy import extra
        os = extra.make_raw_ostream_for_printing()
        self.print_(os)
        return os.str()

    getContainedType = Method(ptr(Type), cast(int, Unsigned))
    getNumContainedTypes = Method(cast(int, Unsigned))

    getArrayNumElements = Method(cast(Uint64, int))
    getArrayElementType = Method(ptr(Type))

    getVectorNumElements = Method(cast(Unsigned, int))
    getVectorElementType = Method(ptr(Type))

    getPointerElementType = Method(ptr(Type))
    getPointerAddressSpace = Method(cast(Unsigned, int))
    getPointerTo = Method(ptr(PointerType), cast(int, Unsigned))


@IntegerType
class IntegerType:
    _downcast_ = Type


@CompositeType
class CompositeType:
    _downcast_ = Type

@SequentialType
class SequentialType:
    _downcast_ = Type

@ArrayType
class ArrayType:
    _downcast_ = Type
    getNumElements = Method(cast(Uint64, int))
    get = StaticMethod(ptr(ArrayType), ptr(Type), cast(int, Uint64))
    isValidElementType = StaticMethod(cast(Bool, bool), ptr(Type))

@PointerType
class PointerType:
    _downcast_ = Type
    getAddressSpace = Method(cast(Unsigned, int))
    get = StaticMethod(ptr(PointerType), ptr(Type), cast(int, Unsigned))
    getUnqual = StaticMethod(ptr(PointerType), ptr(Type))
    isValidElementType = StaticMethod(cast(Bool, bool), ptr(Type))

@VectorType
class VectorType:
    _downcast_ = Type
    getNumElements = Method(cast(Unsigned, int))
    getBitWidth = Method(cast(Unsigned, int))
    get = StaticMethod(ptr(VectorType), ptr(Type), cast(int, Unsigned))
    getInteger = StaticMethod(ptr(VectorType), ptr(VectorType))
    getExtendedElementVectorType = StaticMethod(ptr(VectorType),
                                                ptr(VectorType))
    getTruncatedElementVectorType = StaticMethod(ptr(VectorType),
                                                 ptr(VectorType))
    isValidElementType = StaticMethod(cast(Bool, bool), ptr(Type))

@StructType
class StructType:
    _downcast_ = Type
    isPacked = Method(cast(Bool, bool))
    isLiteral = Method(cast(Bool, bool))
    isOpaque = Method(cast(Bool, bool))
    hasName = Method(cast(Bool, bool))
    getName = Method(cast(StringRef, str))
    setName = Method(Void, cast(str, StringRef))
    setBody = CustomMethod('StructType_setBody',
                           PyObjectPtr, # None
                           PyObjectPtr, # ArrayRef<Type*>
                           cast(bool, Bool),
                           ).require_only(1)
    getNumElements = Method(cast(Unsigned, int))
    getElementType = Method(ptr(Type), cast(int, Unsigned))

    create = StaticMethod(ptr(StructType),
                          ref(LLVMContext),
                          cast(str, StringRef),
                          ).require_only(1)

    get = CustomStaticMethod('StructType_get',
                             PyObjectPtr,           # StructType*
                             ref(LLVMContext),
                             PyObjectPtr,           # ArrayRef <Type*> elements
                             cast(bool, Bool),      # is packed
                             ).require_only(2)

    isLayoutIdentical = Method(cast(Bool, bool), # identical?
                               ptr(StructType))  # other

    isValidElementType = StaticMethod(cast(Bool, bool), ptr(Type))

