from binding import *
from .namespace import llvm
from .Value import Value, User
from .Value import Constant, UndefValue, ConstantInt, ConstantFP, ConstantArray
from .Value import ConstantStruct, ConstantVector, ConstantVector
from .Value import ConstantDataSequential, ConstantDataArray, ConstantExpr
from .LLVMContext import LLVMContext
from .ADT.StringRef import StringRef
from .ADT.SmallVector import SmallVector_Value, SmallVector_Unsigned
from .Type import Type, IntegerType, ArrayType, StructType
from .Instruction import CmpInst

@Constant
class Constant:
    _downcast_ = Value, User

    isNullValue = Method(cast(bool, Bool))
    isAllOnesValue = Method(cast(bool, Bool))
    isNegativeZeroValue = Method(cast(bool, Bool))
    #isZeroValue = Method(cast(bool, Bool))
    canTrap = Method(cast(bool, Bool))
    isThreadDependent = Method(cast(bool, Bool))
    isConstantUsed = Method(cast(bool, Bool))

    _getAggregateElement_by_int = Method(ptr(Constant), cast(int, Unsigned))
    _getAggregateElement_by_int.realname = 'getAggregateElement'
    _getAggregateElement_by_const = Method(ptr(Constant), ptr(Constant))
    _getAggregateElement_by_const.realname = 'getAggregateElement'

    @CustomPythonMethod
    def getAggregateElement(self, elt):
        if isinstance(elt, Constant):
            return self._getAggregateElement_by_const(elt)
        else:
            return self._getAggregateElement_by_int(elt)


    removeDeadConstantUsers = Method()

    getNullValue = StaticMethod(ptr(Constant), ptr(Type))
    getAllOnesValue = StaticMethod(ptr(Constant), ptr(Type))
    getIntegerValue = CustomStaticMethod('Constant_getIntegerValue',
                                         PyObjectPtr, # ptr(Constant),
                                         ptr(Type),
                                         PyObjectPtr)



@UndefValue
class UndefValue:
    getSequentialElement = Method(ptr(UndefValue))
    getStructElement = Method(ptr(UndefValue), cast(int, Unsigned))

    _getElementValue_by_const = Method(ptr(UndefValue), ptr(Constant))
    _getElementValue_by_const.realname = 'getElementValue'

    _getElementValue_by_int = Method(ptr(UndefValue), cast(int, Unsigned))
    _getElementValue_by_int.realname = 'getElementValue'

    @CustomPythonMethod
    def getElementValue(self, idx):
        if isinstance(idx, Constant):
            return self._getElementValue_by_const(idx)
        else:
            return self._getElementValue_by_int(idx)

    destroyConstant = Method()

    get = StaticMethod(ptr(UndefValue), ptr(Type))



@ConstantInt
class ConstantInt:
    _downcast_ = Constant, User, Value

    get = StaticMethod(ptr(ConstantInt),
                       ptr(IntegerType),
                       cast(int, Uint64),
                       cast(bool, Bool),
                       ).require_only(2)
    isValueValidForType = StaticMethod(cast(Bool, bool),
                                       ptr(Type),
                                       cast(int, Int64))
    getZExtValue = Method(cast(Uint64, int))
    getSExtValue = Method(cast(Int64, int))


@ConstantFP
class ConstantFP:
    _downcast_ = Constant, User, Value

    get = StaticMethod(ptr(Constant), ptr(Type), cast(float, Double))
    getNegativeZero = StaticMethod(ptr(ConstantFP), ptr(Type))
    getInfinity = StaticMethod(ptr(ConstantFP), ptr(Type), cast(bool, Bool))

    isZero = Method(cast(Bool, bool))
    isNegative = Method(cast(Bool, bool))
    isNaN = Method(cast(Bool, bool))



@ConstantArray
class ConstantArray:
    _downcast_ = Constant, User, Value

    get = CustomStaticMethod('ConstantArray_get',
                             PyObjectPtr, # ptr(Constant),
                             ptr(ArrayType),
                             PyObjectPtr,    # Constants
                             )


@ConstantStruct
class ConstantStruct:
    _downcast_ = Constant, User, Value

    get = CustomStaticMethod('ConstantStruct_get',
                             PyObjectPtr, # ptr(Constant)
                             ptr(StructType),
                             PyObjectPtr, # Constants
                             )
    getAnon = CustomStaticMethod('ConstantStruct_getAnon',
                                 PyObjectPtr, # ptr(Constant)
                                 PyObjectPtr, # constants
                                 cast(bool, Bool), # packed
                                 ).require_only(1)


@ConstantVector
class ConstantVector:
    _downcast_ = Constant, User, Value

    get = CustomStaticMethod('ConstantVector_get',
                             PyObjectPtr, # ptr(Constant)
                             PyObjectPtr, # constants
                             )


@ConstantDataSequential
class ConstantDataSequential:
    _downcast_ = Constant, User, Value


@ConstantDataArray
class ConstantDataArray:
    _downcast_ = Constant, User, Value

    getString = StaticMethod(ptr(Constant),
                             ref(LLVMContext),
                             cast(str, StringRef),
                             cast(bool, Bool)
                             ).require_only(2)



def _factory(*args):
    return StaticMethod(ptr(Constant), *args)

def _factory_const(*args):
    return _factory(ptr(Constant), *args)

def _factory_const2(*args):
    return _factory(ptr(Constant), ptr(Constant), *args)

def _factory_const_nuw_nsw():
    return _factory_const(cast(bool, Bool), cast(bool, Bool)).require_only(1)

def _factory_const2_nuw_nsw():
    return _factory_const2(cast(bool, Bool), cast(bool, Bool)).require_only(2)

def _factory_const2_exact():
    return _factory_const2(cast(bool, Bool)).require_only(2)

def _factory_const_type():
    return _factory_const(ptr(Type))

@ConstantExpr
class ConstantExpr:
    _downcast_ = Constant, User, Value

    getAlignOf = _factory(ptr(Type))
    getSizeOf = _factory(ptr(Type))
    getOffsetOf = _factory(ptr(Type), ptr(Constant))
    getNeg = _factory_const_nuw_nsw()
    getFNeg = _factory_const()
    getNot = _factory_const()
    getAdd = _factory_const2_nuw_nsw()
    getFAdd = _factory_const2()
    getSub = _factory_const2_nuw_nsw()
    getFSub = _factory_const2()
    getMul = _factory_const2_nuw_nsw()
    getFMul = _factory_const2()
    getUDiv = _factory_const2_exact()
    getSDiv = _factory_const2_exact()
    getFDiv = _factory_const2()
    getURem = _factory_const2()
    getSRem = _factory_const2()
    getFRem = _factory_const2()
    getAnd = _factory_const2()
    getOr = _factory_const2()
    getXor = _factory_const2()
    getShl = _factory_const2_nuw_nsw()
    getLShr = _factory_const2_exact()
    getAShr = _factory_const2_exact()
    getTrunc = _factory_const_type()
    getSExt = _factory_const_type()
    getZExt = _factory_const_type()
    getFPTrunc = _factory_const_type()
    getFPExtend = _factory_const_type()
    getUIToFP = _factory_const_type()
    getSIToFP = _factory_const_type()
    getFPToUI = _factory_const_type()
    getFPToSI = _factory_const_type()
    getPtrToInt = _factory_const_type()
    getIntToPtr = _factory_const_type()
    getBitCast = _factory_const_type()

    getCompare = _factory(CmpInst.Predicate, ptr(Constant), ptr(Constant))
    getICmp = _factory(CmpInst.Predicate, ptr(Constant), ptr(Constant))
    getFCmp = _factory(CmpInst.Predicate, ptr(Constant), ptr(Constant))

    getPointerCast = _factory_const_type()
    getIntegerCast = _factory_const(ptr(Type), cast(bool, Bool))
    getFPCast = _factory_const_type()
    getSelect = _factory(ptr(Constant), ptr(Constant), ptr(Constant))


    _getGEP = _factory(ptr(Constant), ref(SmallVector_Value), cast(bool, Bool))
    _getGEP.require_only(2)
    _getGEP.realname = 'getGetElementPtr'

    @CustomPythonStaticMethod
    def getGetElementPtr(*args):
        from llvmpy import extra
        args = list(args)
        valuelist = args[1]
        args[1] = extra.make_small_vector_from_values(*valuelist)
        return ConstantExpr._getGEP(*args)

    getExtractElement = _factory_const2()
    getInsertElement = _factory_const2(ptr(Constant))
    getShuffleVector = _factory_const2(ptr(Constant))

    _getExtractValue = _factory(ptr(Constant), ref(SmallVector_Unsigned))
    _getExtractValue.realname = 'getExtractValue'

    @CustomPythonStaticMethod
    def getExtractValue(*args):
        from llvmpy import extra
        args = list(args)
        valuelist = args[1]
        args[1] = extra.make_small_vector_from_unsigned(*valuelist)
        return ConstantExpr._getExtractValue(*args)

    _getInsertValue = _factory(ptr(Constant), ptr(Constant),
                               ref(SmallVector_Unsigned))
    _getInsertValue.realname = 'getInsertValue'

    @CustomPythonStaticMethod
    def getInsertValue(*args):
        from llvmpy import extra
        args = list(args)
        valuelist = args[2]
        args[1] = extra.make_small_vector_from_unsigned(*valuelist)
        return ConstantExpr._getInsertValue(*args)

    getOpcode = Method(cast(Unsigned, int))
    getOpcodeName = Method(cast(ConstCharPtr, str))
    isCast = Method(cast(Bool, bool))
    isCompare = Method(cast(Bool, bool))
    hasIndices = Method(cast(Bool, bool))
    isGEPWithNoNotionalOverIndexing = Method(cast(Bool, bool))

