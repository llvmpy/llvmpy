from binding import *
from .namespace import llvm
from .Pass import ImmutablePass

DataLayout = llvm.Class(ImmutablePass)
StructLayout = llvm.Class()

from .LLVMContext import LLVMContext
from .ADT.StringRef import StringRef
from .Module import Module
from .Type import Type, IntegerType, StructType
from .ADT.SmallVector import SmallVector_Value
from .GlobalVariable import GlobalVariable


@DataLayout
class DataLayout:
    if LLVM_VERSION >= (3, 3):
        _include_ = 'llvm/IR/DataLayout.h'
    else:
        _include_ = 'llvm/DataLayout.h'

    _new_string = Constructor(cast(str, StringRef))
    _new_module = Constructor(ptr(Module))

    @CustomPythonStaticMethod
    def new(arg):
        if isinstance(arg, Module):
            return DataLayout._new_module(arg)
        else:
            return DataLayout._new_string(arg)

    isLittleEndian = Method(cast(Bool, bool))
    isBigEndian = Method(cast(Bool, bool))

    getStringRepresentation = Method(cast(StdString, str))

    @CustomPythonMethod
    def __str__(self):
        return self.getStringRepresentation()

    isLegalInteger = Method(cast(Bool, bool), cast(int, Unsigned))
    isIllegalInteger = Method(cast(Bool, bool), cast(int, Unsigned))
    exceedsNaturalStackAlignment = Method(cast(Bool, bool), cast(int, Unsigned))
    fitsInLegalInteger = Method(cast(Bool, bool), cast(int, Unsigned))

    getPointerABIAlignment = Method(cast(Unsigned, int),
                                    cast(int, Unsigned)).require_only(0)
    getPointerPrefAlignment = Method(cast(Unsigned, int),
                                     cast(int, Unsigned)).require_only(0)
    getPointerSize = Method(cast(Unsigned, int),
                            cast(int, Unsigned)).require_only(0)
    getPointerSizeInBits = Method(cast(Unsigned, int),
                                  cast(int, Unsigned)).require_only(0)

    getTypeSizeInBits = Method(cast(Uint64, int), ptr(Type))
    getTypeStoreSize = Method(cast(Uint64, int), ptr(Type))
    getTypeStoreSizeInBits = Method(cast(Uint64, int), ptr(Type))
    getTypeAllocSize = Method(cast(Uint64, int), ptr(Type))
    getTypeAllocSizeInBits = Method(cast(Uint64, int), ptr(Type))

    getABITypeAlignment = Method(cast(Unsigned, int), ptr(Type))
    getABIIntegerTypeAlignment = Method(cast(Unsigned, int), cast(int, Unsigned))
    getCallFrameTypeAlignment = Method(cast(Unsigned, int), ptr(Type))
    getPrefTypeAlignment = Method(cast(Unsigned, int), ptr(Type))
    getPreferredTypeAlignmentShift = Method(cast(Unsigned, int), ptr(Type))

    _getIntPtrType = Method(ptr(IntegerType),
                            ref(LLVMContext), cast(int, Unsigned))
    _getIntPtrType.require_only(1)
    _getIntPtrType.realname = 'getIntPtrType'

    _getIntPtrType2 = Method(ptr(Type), ptr(Type))
    _getIntPtrType2.realname = 'getIntPtrType'

    @CustomPythonMethod
    def getIntPtrType(self, *args):
        if isinstance(args[0], LLVMContext):
            return self._getIntPtrType(*args)
        else:
            return self._getIntPtrType(*args)

    _getIndexedOffset = Method(cast(Uint64, int), ptr(Type),
                               ref(SmallVector_Value))
    _getIndexedOffset.realname = 'getIndexedOffset'

    @CustomPythonMethod
    def getIndexedOffset(self, *args):
        from llvmpy import extra
        args = list(args)
        args[1] = extra.make_small_vector_from_values(args[1])
        return self.getIndexedOffset(*args)

    getStructLayout = Method(const(ptr(StructLayout)), ptr(StructType))

    getPreferredAlignment = Method(cast(Unsigned, int), ptr(GlobalVariable))
    getPreferredAlignmentLog = Method(cast(Unsigned, int), ptr(GlobalVariable))

@StructLayout
class StructLayout:
    getSizeInBytes = Method(cast(Uint64, int))
    getSizeInBits = Method(cast(Uint64, int))
    getAlignment = Method(cast(Unsigned, int))
    getElementContainingOffset = Method(cast(Unsigned, int), cast(int, Uint64))
    getElementOffset = Method(cast(Uint64, int), cast(int, Unsigned))
    getElementOffsetInBits = Method(cast(Uint64, int), cast(int, Unsigned))
