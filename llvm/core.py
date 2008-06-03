"""Core classes of LLVM.

The llvm.core module contains classes and constants required to build the
in-memory intermediate representation (IR) data structures."""


import llvm   # top-level, for common stuff
import _core  # C wrappers


#===----------------------------------------------------------------------===
# Enumerations
#===----------------------------------------------------------------------===


# type kinds
TYPE_VOID       = 0
TYPE_FLOAT      = 1
TYPE_DOUBLE     = 2
TYPE_X86_FP80   = 3
TYPE_FP128      = 4
TYPE_PPC_FP128  = 5
TYPE_LABEL      = 6
TYPE_INTEGER    = 7
TYPE_FUNCTION   = 8
TYPE_STRUCT     = 9
TYPE_ARRAY      = 10
TYPE_POINTER    = 11
TYPE_OPAQUE     = 12
TYPE_VECTOR     = 13

# calling conventions
CC_C            = 0
CC_FASTCALL     = 8
CC_COLDCALL     = 9
CC_X86_STDCALL  = 64
CC_X86_FASTCALL = 65

# int predicates
IPRED_EQ        = 32
IPRED_NE        = 33
IPRED_UGT       = 34
IPRED_UGE       = 35
IPRED_ULT       = 36
IPRED_ULE       = 37
IPRED_SGT       = 38
IPRED_SGE       = 39
IPRED_SLT       = 40
IPRED_SLE       = 41

# real predicates
RPRED_FALSE     = 0
RPRED_OEQ       = 1
RPRED_OGT       = 2
RPRED_OGE       = 3
RPRED_OLT       = 4
RPRED_OLE       = 5
RPRED_ONE       = 6
RPRED_ORD       = 7
RPRED_UNO       = 8
RPRED_UEQ       = 9
RPRED_UGT       = 10
RPRED_UGE       = 11
RPRED_ULT       = 12
RPRED_ULE       = 13
RPRED_UNE       = 14
RPRED_TRUE      = 15

# linkages
LINKAGE_EXTERNAL    = 0
LINKAGE_LINKONCE    = 1
LINKAGE_WEAK        = 2
LINKAGE_APPENDING   = 3
LINKAGE_INTERNAL    = 4
LINKAGE_DLLIMPORT   = 5
LINKAGE_DLLEXPORT   = 6
LINKAGE_EXTERNAL_WEAK = 7
LINKAGE_GHOST       = 8

# visibility
VISIBILITY_DEFAULT  = 0
VISIBILITY_HIDDEN   = 1
VISIBILITY_PROTECTED = 2

# parameter attributes
ATTR_ZEXT           = 1
ATTR_SEXT           = 2
ATTR_NO_RETURN      = 4
ATTR_IN_REG         = 8
ATTR_STRUCT_RET     = 16
ATTR_NO_UNWIND      = 32
ATTR_NO_ALIAS       = 64
ATTR_BY_VAL         = 128
ATTR_NEST           = 256
ATTR_READ_NONE      = 512
ATTR_READONLY       = 1024


#===----------------------------------------------------------------------===
# Helper functions
#===----------------------------------------------------------------------===


def _check_gen(obj, type, type_str):
    if not isinstance(obj, type):
        type_str = type.__module__ + "." + type.__name__
        msg = "argument must be an instance of llvm.core.%s (or of a class derived from it)" % type_str
        raise TypeError, msg

def _check_is_type(obj):     _check_gen(obj, Type,  "Type")
def _check_is_value(obj):    _check_gen(obj, Value, "Value")
def _check_is_pointer(obj):  _check_gen(obj, Pointer, "Pointer")
def _check_is_constant(obj): _check_gen(obj, Constant, "Constant")
def _check_is_function(obj): _check_gen(obj, Function, "Function")
def _check_is_basic_block(obj): _check_gen(obj, BasicBlock, "BasicBlock")
def _check_is_module_provider(obj): _check_gen(obj, ModuleProvider, "ModuleProvider")

def _unpack_gen(objlist, check_fn):
    for obj in objlist: check_fn(obj)
    return [ obj.ptr for obj in objlist ]

def _unpack_types(objlist):     return _unpack_gen(objlist, _check_is_type)
def _unpack_values(objlist):    return _unpack_gen(objlist, _check_is_value)
def _unpack_constants(objlist): return _unpack_gen(objlist, _check_is_constant)

def _wrapiter(first, next, container, wrapper):
    ptr = first(container)
    while ptr:
        yield wrapper(ptr)
        ptr = next(ptr)

class _dummy_owner(object):

    def __init__(self, ownee):
        ownee._own(self)


#===----------------------------------------------------------------------===
# Module
#===----------------------------------------------------------------------===


class Module(object):
    """A Module instance stores all the information related to an LLVM module. 
       
    Modules are the top level container of all other LLVM Intermediate
    Representation (IR) objects. Each module directly contains a list of
    globals variables, a list of functions, a list of libraries (or
    other modules) this module depends on, a symbol table, and various
    data about the target's characteristics.

    Construct a Module only using the static methods defined below, *NOT*
    using the constructor. A correct usage is:

    module_obj = Module.new('my_module')
    """

    @staticmethod
    def new(id):
        """Create a new Module instance.

        Creates an instance of Module, having the id `id'.
        """
        return Module(_core.LLVMModuleCreateWithName(id))

    def __init__(self, ptr):
        """DO NOT CALL DIRECTLY.

        Use the static method `Module.new' instead.
        """
        self.ptr = ptr
        self.owner = None

    def __del__(self):
        if not self.owner:
            _core.LLVMDisposeModule(self.ptr)

    def __str__(self):
        """Text representation of a module.

        Returns the textual representation (`llvm assembly') of the
        module. Use it like this:

        ll = str(module_obj)
        print module_obj     # same as `print ll'
        """
        return _core.LLVMDumpModuleToString(self.ptr)

    def __eq__(self, rhs):
        if isinstance(rhs, Module):
            return str(self) == str(rhs)
        else:
            return False

    def _own(self, owner):
        assert not self.owner
        self.owner = owner
    
    def _get_target(self):
        return _core.LLVMGetTarget(self.ptr)

    def _set_target(self, value):
        return _core.LLVMSetTarget(self.ptr, value)

    target = property(_get_target, _set_target,
        """The target triple string describing the target host."""
    )

    def _get_data_layout(self):
        return _core.LLVMGetDataLayout(self.ptr)

    def _set_data_layout(self, value):
        _core.LLVMSetDataLayout(self.ptr, value)

    data_layout = property(_get_data_layout, _set_data_layout,
        """The data layout string for the module's target platform.

        The data layout strings is an encoded representation of
        the type sizes and alignments expected by this module.
        """
    )

    def add_type_name(self, name, ty):
        """Map a string to a type.

        Similar to C's struct/typedef declarations. Returns True
        if entry already existed (in which case nothing is changed),
        False otherwise.
        """
        _check_is_type(ty)
        return _core.LLVMAddTypeName(self.ptr, name, ty.ptr) != 0

    def delete_type_name(self, name):
        """Removes a named type.

        Undoes what add_type_name() does.
        """
        _core.LLVMDeleteTypeName(self.ptr, name)

    def add_global_variable(self, ty, name):
        """Add a global variable of given type with given name."""
        return GlobalVariable.new(self, ty, name)

    def get_global_variable_named(self, name):
        """Return a GlobalVariable object for the given name."""
        return GlobalVariable.get(self, name)

    @property
    def global_variables(self):
        """All global variables in this module.

        This property returns a generator that yields GlobalVariable
        objects. Use it like this:
          for gv in module_obj.global_variables:
            # gv is an instance of GlobalVariable
            # do stuff with gv
        """
        return _wrapiter(_core.LLVMGetFirstGlobal, _core.LLVMGetNextGlobal,
            self.ptr, GlobalVariable)

    def add_function(self, ty, name):
        """Add a function of given type with given name."""
        return Function.new(self, ty, name)

    def get_function_named(self, name):
        """Return a Function object representing function with given name."""
        return Function.get(self, name)

    @property
    def functions(self):
        """All functions in this module.

        This property returns a generator that yields Function objects.
        Use it like this:
          for f in module_obj.functions:
            # f is an instance of Function
            # do stuff with f
        """
        return _wrapiter(_core.LLVMGetFirstFunction, 
            _core.LLVMGetNextFunction, self.ptr, Function)

    def verify(self):
        ret = _core.LLVMVerifyModule(self.ptr)
        if ret != "":
            raise llvm.LLVMException, ret


#===----------------------------------------------------------------------===
# Types
#===----------------------------------------------------------------------===


class Type(object):

    @staticmethod
    def int(bits=32):
        if bits == 1:
            return _make_type(_core.LLVMInt1Type(), TYPE_INTEGER)
        elif bits == 8:
            return _make_type(_core.LLVMInt2Type(), TYPE_INTEGER)
        elif bits == 16:
            return _make_type(_core.LLVMInt16Type(), TYPE_INTEGER)
        elif bits == 32:
            return _make_type(_core.LLVMInt32Type(), TYPE_INTEGER)
        elif bits == 64:
            return _make_type(_core.LLVMInt64Type(), TYPE_INTEGER)
        else:
            return _make_type(_core.LLVMIntType(bits), TYPE_INTEGER)
    
    @staticmethod
    def float():
        return _make_type(_core.LLVMFloatType(), TYPE_FLOAT)

    @staticmethod
    def double():
        return _make_type(_core.LLVMDoubleType(), TYPE_DOUBLE)

    @staticmethod
    def x86_fp80():
        return _make_type(_core.LLVMX86FP80Type(), TYPE_X86_FP80)

    @staticmethod
    def fp128():
        return _make_type(_core.LLVMFP128Type(), TYPE_FP128)

    @staticmethod
    def ppc_fp128():
        return _make_type(_core.LLVMPPCFP128Type(), TYPE_PPC_FP128)

    @staticmethod
    def function(return_ty, param_tys, var_arg=False):
        _check_is_type(return_ty)
        var_arg = 1 if var_arg else 0 # convert to int
        params = _unpack_types(param_tys)
        return _make_type(_core.LLVMFunctionType(return_ty.ptr, params, var_arg), TYPE_FUNCTION)

    @staticmethod
    def struct(element_tys): # not packed
        elems = _unpack_types(element_tys)
        return _make_type(_core.LLVMStructType(elems, 0), TYPE_STRUCT)

    @staticmethod
    def struct_packed(element_tys):
        elems = _unpack_types(element_tys)
        return _make_type(_core.LLVMStructType(elems, 1), TYPE_STRUCT)

    @staticmethod
    def array(element_ty, count):
        _check_is_type(element_ty)
        return _make_type(_core.LLVMArrayType(element_ty.ptr, count), TYPE_ARRAY)

    @staticmethod
    def pointer(pointee_ty, addr_space=0):
        _check_is_type(pointee_ty)
        return _make_type(_core.LLVMPointerType(pointee_ty.ptr, addr_space), TYPE_POINTER)

    @staticmethod
    def vector(element_ty, count):
        _check_is_type(element_ty)
        return _make_type(_core.LLVMVectorType(element_ty.ptr, count), TYPE_VECTOR)

    @staticmethod
    def void():
        return _make_type(_core.LLVMVoidType(), TYPE_VOID)

    @staticmethod
    def label():
        return _make_type(_core.LLVMLabelType(), TYPE_LABEL)

    @staticmethod
    def opaque():
        return _make_type(_core.LLVMOpaqueType(), TYPE_OPAQUE)

    def __init__(self, ptr, kind):
        self.ptr = ptr
        self.kind = kind

    def __str__(self):
        return _core.LLVMDumpTypeToString(self.ptr)

    def __eq__(self, rhs):
        if isinstance(rhs, Type):
            return str(self) == str(rhs)
        else:
            return False

    def refine(self, dest):
        """Refine the abstract type represented by self to a concrete class.

        This object is no longer valid after refining, so do not hold references
        to it after calling."""

        _check_is_type(dest)
        _core.LLVMRefineType(self.ptr, dest.ptr)
        self.ptr = None


class IntegerType(Type):

    def __init__(self, ptr, kind):
        Type.__init__(self, ptr, kind)

    @property
    def width(self):
        return _core.LLVMGetIntTypeWidth(self.ptr)


class FunctionType(Type):

    def __init__(self, ptr, kind):
        Type.__init__(self, ptr, kind)

    @property
    def return_type(self):
        ptr  = _core.LLVMGetReturnType(self.ptr)
        kind = _core.LLVMGetTypeKind(ptr)
        return _make_type(ptr, kind)

    @property
    def vararg(self):
        return _core.LLVMIsFunctionVarArg(self.ptr) != 0

    @property
    def args(self):
        pp = _core.LLVMGetFunctionTypeParams(self.ptr)
        return [ _make_type(p, _core.LLVMGetTypeKind(p)) for p in pp ]

    @property
    def arg_count(self):
        return _core.LLVMCountParamTypes(self.ptr)


class StructType(Type):

    def __init__(self, ptr, kind):
        Type.__init__(self, ptr, kind)

    @property
    def element_count(self):
        return _core.LLVMCountStructElementTypes(self.ptr)

    @property
    def element_types(self):
        pp = _core.LLVMGetStructElementTypes(self.ptr)
        return [ _make_type(p, _core.LLVMGetTypeKind(p)) for p in pp ]

    @property
    def packed(self):
        return _core.LLVMIsPackedStruct(self.ptr) != 0


class ArrayType(Type):

    def __init__(self, ptr, kind):
        Type.__init__(self, ptr, kind)

    @property
    def element_type(self):
        ptr  = _core.LLVMGetElementType(self.ptr)
        kind = _core.LLVMGetTypeKind(ptr)
        return _make_type(ptr, kind)

    @property
    def element_count(self):
        return _core.LLVMGetArrayLength(self.ptr)


class PointerType(Type):

    def __init__(self, ptr, kind):
        Type.__init__(self, ptr, kind)

    @property
    def address_space(self):
        return _core.LLVMGetPointerAddressSpace(self.ptr)


class VectorType(Type):

    def __init__(self, ptr, kind):
        Type.__init__(self, ptr, kind)

    @property
    def element_type(self):
        ptr  = _core.LLVMGetElementType(self.ptr)
        kind = _core.LLVMGetTypeKind(ptr)
        return _make_type(ptr, kind)

    @property
    def element_count(self):
        return _core.LLVMGetVectorSize(self.ptr)


def _make_type(ptr, kind):
    if kind == TYPE_INTEGER:
        return IntegerType(ptr, kind)
    elif kind == TYPE_FUNCTION:
        return FunctionType(ptr, kind)
    elif kind == TYPE_STRUCT:
        return StructType(ptr, kind)
    elif kind == TYPE_ARRAY:
        return ArrayType(ptr, kind)
    elif kind == TYPE_POINTER:
        return PointerType(ptr, kind)
    elif kind == TYPE_VECTOR:
        return VectorType(ptr, kind)
    else:
        return Type(ptr, kind)


#===----------------------------------------------------------------------===
# Type Handle
#===----------------------------------------------------------------------===


class TypeHandle(object):

    @staticmethod
    def new(abstract_ty):
        _check_is_type(abstract_ty)
        return TypeHandle(_core.LLVMCreateTypeHandle(abstract_ty.ptr))

    def __init__(self, ptr):
        self.ptr = ptr

    def __del__(self):
        _core.LLVMDisposeTypeHandle(self.ptr)

    @property
    def type(self):
        ptr = _core.LLVMResolveTypeHandle(self.ptr)
        return _make_type(ptr, _core.LLVMGetTypeKind(ptr))


#===----------------------------------------------------------------------===
# Values
#===----------------------------------------------------------------------===


class Value(object):

    def __init__(self, ptr):
        self.ptr = ptr

    def __str__(self):
        return _core.LLVMDumpValueToString(self.ptr)

    def __eq__(self, rhs):
        if isinstance(rhs, Value):
            return str(self) == str(rhs)
        else:
            return False

    def get_name(self):
        return _core.LLVMGetValueName(self.ptr)

    def set_name(self, value):
        return _core.LLVMSetValueName(self.ptr, value)

    name = property(get_name, set_name)

    @property
    def type(self):
        ptr  = _core.LLVMTypeOf(self.ptr)
        kind = _core.LLVMGetTypeKind(ptr)
        return _make_type(ptr, kind)


class Constant(Value):

    @staticmethod
    def null(ty):
        _check_is_type(ty)
        return Constant(_core.LLVMConstNull(ty.ptr));
        
    @staticmethod
    def all_ones(ty):
        _check_is_type(ty)
        return Constant(_core.LLVMConstAllOnes(ty.ptr));
        
    @staticmethod
    def undef(ty):
        _check_is_type(ty)
        return Constant(_core.LLVMGetUndef(ty.ptr));

    @staticmethod
    def int(ty, value):
        _check_is_type(ty)
        return Constant(_core.LLVMConstInt(ty.ptr, value, 0))

    @staticmethod
    def int_signextend(ty, value):
        _check_is_type(ty)
        return Constant(_core.LLVMConstInt(ty.ptr, value, 1))

    @staticmethod
    def real(ty, value):
        _check_is_type(ty)
        if isinstance(value, str):
            return Constant(_core.LLVMConstRealOfString(ty.ptr, value))
        else:
            return Constant(_core.LLVMConstReal(ty.ptr, value))

    @staticmethod
    def string(strval): # dont_null_terminate=True
        return Constant(_core.LLVMConstString(strval, 1))
        
    @staticmethod
    def stringz(strval): # dont_null_terminate=False
        return Constant(_core.LLVMConstString(strval, 0))

    @staticmethod
    def array(ty, consts):
        _check_is_type(ty)
        const_ptrs = _unpack_constants(consts)
        return Constant(_core.LLVMConstArray(ty.ptr, const_ptrs))
        
    @staticmethod
    def struct(consts): # not packed
        const_ptrs = _unpack_constants(consts)
        return Constant(_core.LLVMConstStruct(consts, 0))
    
    @staticmethod
    def struct_packed(consts):
        const_ptrs = _unpack_constants(consts)
        return Constant(_core.LLVMConstStruct(consts, 1))
    
    @staticmethod
    def vector(consts):
        const_ptrs = _unpack_constants(consts)
        return Constant(_core.LLVMConstVector(const_ptrs))

    @staticmethod
    def sizeof(ty):
        _check_is_type(ty)
        return Constant(_core.LLVMSizeOf(ty.ptr))

    def __init__(self, ptr):
        self.ptr = ptr
        
    def neg(self):
        return Constant(_core.LLVMConstNeg(self.ptr))
        
    def not_(self):
        return Constant(_core.LLVMConstNot(self.ptr))
        
    def add(self, rhs):
        _check_is_constant(rhs)
        return Constant(_core.LLVMConstAdd(self.ptr, rhs.ptr))

    def sub(self, rhs):
        _check_is_constant(rhs)
        return Constant(_core.LLVMConstSub(self.ptr, rhs.ptr))

    def mul(self, rhs):
        _check_is_constant(rhs)
        return Constant(_core.LLVMConstMul(self.ptr, rhs.ptr))

    def udiv(self, rhs):
        _check_is_constant(rhs)
        return Constant(_core.LLVMConstUDiv(self.ptr, rhs.ptr))

    def sdiv(self, rhs):
        _check_is_constant(rhs)
        return Constant(_core.LLVMConstSDiv(self.ptr, rhs.ptr))

    def fdiv(self, rhs):
        _check_is_constant(rhs)
        return Constant(_core.LLVMConstFDiv(self.ptr, rhs.ptr))

    def urem(self, rhs):
        _check_is_constant(rhs)
        return Constant(_core.LLVMConstURem(self.ptr, rhs.ptr))

    def srem(self, rhs):
        _check_is_constant(rhs)
        return Constant(_core.LLVMConstSRem(self.ptr, rhs.ptr))

    def and_(self, rhs):
        _check_is_constant(rhs)
        return Constant(_core.LLVMConstAnd(self.ptr, rhs.ptr))

    def or_(self, rhs):
        _check_is_constant(rhs)
        return Constant(_core.LLVMConstOr(self.ptr, rhs.ptr))

    def xor(self, rhs):
        _check_is_constant(rhs)
        return Constant(_core.LLVMConstXor(self.ptr, rhs.ptr))

    def icmp(self, int_pred, rhs):
        _check_is_constant(rhs)
        return Constant(_core.LLVMConstICmp(self.ptr, int_pred, rhs.ptr))

    def fcmp(self, real_pred, rhs):
        _check_is_constant(rhs)
        return Constant(_core.LLVMConstFCmp(self.ptr, real_pred, rhs.ptr))

    def shl(self, rhs):
        _check_is_constant(rhs)
        return Constant(_core.LLVMConstShl(self.ptr, rhs.ptr))

    def lshr(self, rhs):
        _check_is_constant(rhs)
        return Constant(_core.LLVMConstLShr(self.ptr, rhs.ptr))

    def ashr(self, rhs):
        _check_is_constant(rhs)
        return Constant(_core.LLVMConstAShr(self.ptr, rhs.ptr))

    def gep(self, indices):
        index_ptrs = _unpack_constants(indices)
        return Constant(_core.LLVMConstGEP(self.ptr, index_ptrs))
    
    def trunc(self, ty):
        _check_is_type(ty)
        return Constant(_core.LLVMConstTrunc(self.ptr, ty.ptr))

    def sext(self, ty):
        _check_is_type(ty)
        return Constant(_core.LLVMConstSExt(self.ptr, ty.ptr))

    def zext(self, ty):
        _check_is_type(ty)
        return Constant(_core.LLVMConstZExt(self.ptr, ty.ptr))

    def fptrunc(self, ty):
        _check_is_type(ty)
        return Constant(_core.LLVMConstFPTrunc(self.ptr, ty.ptr))

    def fpext(self, ty):
        _check_is_type(ty)
        return Constant(_core.LLVMConstFPExt(self.ptr, ty.ptr))

    def uitofp(self, ty):
        _check_is_type(ty)
        return Constant(_core.LLVMConstUIToFP(self.ptr, ty.ptr))

    def sitofp(self, ty):
        _check_is_type(ty)
        return Constant(_core.LLVMConstSIToFP(self.ptr, ty.ptr))

    def fptoui(self, ty):
        _check_is_type(ty)
        return Constant(_core.LLVMConstFPToUI(self.ptr, ty.ptr))

    def fptosi(self, ty):
        _check_is_type(ty)
        return Constant(_core.LLVMConstFPToSI(self.ptr, ty.ptr))

    def ptrtoint(self, ty):
        _check_is_type(ty)
        return Constant(_core.LLVMConstPtrToInt(self.ptr, ty.ptr))

    def inttoptr(self, ty):
        _check_is_type(ty)
        return Constant(_core.LLVMConstIntToPtr(self.ptr, ty.ptr))

    def bitcast(self, ty):
        _check_is_type(ty)
        return Constant(_core.LLVMConstBitCast(self.ptr, ty.ptr))

    def select(self, true_const, false_const):
        _check_is_constant(true_const)
        _check_is_constant(false_const)
        return Constant(_core.LLVMConstSelect(self.ptr, true_const.ptr, false_const.ptr))

    def extract(self, index): # note: self must be a _vector_ constant
        _check_is_constant(index)
        return Constant(_core.LLVMConstExtractElement(self.ptr, index.ptr))

    def insert(self, value, index): # note: self must be a _vector_ constant
        _check_is_constant(value)
        _check_is_constant(index)
        return Constant(_core.LLVMConstInsertElement(self.ptr, value.ptr, index.ptr))

    def shuffle(self, vector_b, mask): # note: self must be a _vector_ constant
        _check_is_constant(vector_b)   # note: vector_b must be a _vector_ constant
        _check_is_constant(mask)
        return Constant(_core.LLVMConstShuffleVector(self.ptr, vector_b.ptr, mask.ptr))

    
class GlobalValue(Value):

    def __init__(self, ptr):
        self.ptr = ptr

    def get_linkage(self): return _core.LLVMGetLinkage(self.ptr)
    def set_linkage(self, value): _core.LLVMSetLinkage(self.ptr, value)
    linkage = property(get_linkage, set_linkage)

    def get_section(self): return _core.LLVMGetSection(self.ptr)
    def set_section(self, value): return _core.LLVMSetSection(self.ptr, value)
    section = property(get_section, set_section)
    
    def get_visibility(self): return _core.LLVMGetVisibility(self.ptr)
    def set_visibility(self, value): return _core.LLVMSetVisibility(self.ptr, value)
    visibility = property(get_visibility, set_visibility)

    def get_alignment(self): return _core.LLVMGetAlignment(self.ptr)
    def set_alignment(self, value): return _core.LLVMSetAlignment(self.ptr, value)
    alignment = property(get_alignment, set_alignment)

    @property
    def is_declaration(self):
        return _core.LLVMIsDeclaration(self.ptr)

    @property
    def module(self):
        mod = Module(_core.LLVMGetGlobalParent(self.ptr))
        owner = _dummy_owner(mod)
        return mod


class GlobalVariable(GlobalValue):

    @staticmethod
    def new(module, ty, name):
        _check_is_type(ty)
        return GlobalVariable(_core.LLVMAddGlobal(module.ptr, ty.ptr, name))

    @staticmethod
    def get(module, name):
        return GlobalVariable(_core.LLVMGetNamedGlobal(module.ptr, name))

    def __init__(self, ptr):
        GlobalValue.__init__(self, ptr)

    def delete(self):
        _core.LLVMDeleteGlobal(self.ptr)
        self.ptr = None

    def get_initializer(self):
        if _core.LLVMHasInitializer(self.ptr):
            return Constant(_core.LLVMGetInitializer(self.ptr))
        else:
            return None

    def set_initializer(self, const):
        _check_is_constant(const)
        _core.LLVMSetInitializer(self.ptr, const.ptr)

    initializer = property(get_initializer, set_initializer)

    def get_is_global_constant(self):
        return _core.LLVMIsGlobalConstant(self.ptr)

    def set_is_global_constant(self, value):
        value = 1 if value else 0
        _core.LLVMSetGlobalConstant(self.ptr, value)

    global_constant = property(get_is_global_constant, set_is_global_constant)


class Argument(Value):

    def __init__(self, ptr):
        Value.__init__(self, ptr)

    def add_attribute(self, attr):
        _core.LLVMAddParamAttr(self.ptr, attr)

    def remove_attribute(self, attr):
        _core.LLVMRemoveParamAttr(self.ptr, attr)

    def set_alignment(self, align):
        _core.LLVMSetParamAlignment(self.ptr, align)

    @property
    def function(self):
        return Function(_core.LLVMGetParamParent(self.ptr))


class Function(GlobalValue):

    @staticmethod
    def new(module, func_ty, name):
        return Function(_core.LLVMAddFunction(module.ptr, name, func_ty.ptr))

    @staticmethod
    def get(module, name):
        return Function(_core.LLVMGetNamedFunction(module.ptr, name))
    
    def __init__(self, ptr):
        GlobalValue.__init__(self, ptr)

    def delete(self):
        _core.LLVMDeleteFunction(self.ptr)
        self.ptr = None

    @property
    def intrinsic_id(self):
        return _core.LLVMGetIntrinsicID(self.ptr)

    def get_calling_convention(self): return _core.LLVMGetFunctionCallConv(self.ptr)
    def set_calling_convention(self, value): _core.LLVMSetFunctionCallConv(self.ptr, value)
    calling_convention = property(get_calling_convention, set_calling_convention)

    def get_collector(self): return _core.LLVMGetCollector(self.ptr)
    def set_collector(self, value): _core.LLVMSetCollector(self.ptr, value)
    collector = property(get_collector, set_collector)

    @property
    def args(self):
        return _wrapiter(_core.LLVMGetFirstParam, _core.LLVMGetNextParam,
            self.ptr, Argument)

    @property
    def basic_block_count(self):
        return _core.LLVMCountBasicBlocks(self.ptr)

    def get_entry_basic_block(self):
        return BasicBlock(_core.LLVMGetEntryBasicBlock(self.ptr))

    def append_basic_block(self, name):
        return BasicBlock(_core.LLVMAppendBasicBlock(self.ptr, name))

    @property
    def basic_blocks(self):
        return _wrapiter(_core.LLVMGetFirstBasicBlock, 
            _core.LLVMGetNextBasicBlock, self.ptr, BasicBlock)

    def verify(self):
        return _core.LLVMVerifyFunction(self.ptr) != 0


#===----------------------------------------------------------------------===
# Instruction
#===----------------------------------------------------------------------===

class Instruction(Value):

    def __init__(self, ptr):
        Value.__init__(self, ptr)

    @property
    def basic_block(self):
        return BasicBlock(_core.LLVMGetInstructionParent(self.ptr))


class CallOrInvokeInstruction(Instruction):

    def __init__(self, ptr):
        Instruction.__init__(self, ptr)

    def get_calling_convention(self): return _core.LLVMGetFunctionCallConv(self.ptr)
    def set_calling_convention(self, value): _core.LLVMSetFunctionCallConv(self.ptr, value)
    calling_convention = property(get_calling_convention, set_calling_convention)

    def add_parameter_attribute(self, idx, attr):
        _core.LLVMAddInstrParamAttr(self.ptr, idx, attr)

    def remove_parameter_attribute(self, idx, attr):
        _core.LLVMRemoveInstrParamAttr(self.ptr, idx, attr)

    def set_parameter_alignment(self, idx, align):
        _core.LLVMSetInstrParamAlignment(self.ptr, idx, align)


class PHINode(Instruction):

    def __init__(self, ptr):
        Instruction.__init__(self, ptr)

    @property
    def incoming_count(self):
        return _core.LLVMCountIncoming(self.ptr)

    def add_incoming(self, value, block):
        _check_is_value(value)
        _check_is_basic_block(block)
        _core.LLVMAddIncoming1(self.ptr, value.ptr, block.ptr)

    def get_incoming_value(self, idx):
        return Value(_core.LLVMGetIncomingValue(self.ptr, idx))

    def get_incoming_block(self, idx):
        return BasicBlock(_core.LLVMGetIncomingBlock(self.ptr, idx))


class SwitchInstruction(Instruction):

    def __init__(self, ptr):
        Instruction.__init__(self, ptr)

    def add_case(self, const, bblk):
        _check_is_constant(const) # and has to be an int too
        _check_is_basic_block(bblk)
        _core.LLVMAddCase(self.ptr, const.ptr, bblk.ptr)


#===----------------------------------------------------------------------===
# Basic block
#===----------------------------------------------------------------------===


class BasicBlock(Value):

    def __init__(self, ptr):
        self.ptr = ptr

    def insert_before(self, name):
        return BasicBlock(_core.LLVMInsertBasicBlock(self.ptr, name))

    def delete(self):
        _core.LLVMDeleteBasicBlock(self.ptr)
        self.ptr = None

    @property
    def function(self):
        return Function(_core.LLVMGetBasicBlockParent(self.ptr))

    @property
    def instructions(self):
        return _wrapiter(_core.LLVMGetFirstInstruction,
            _core.LLVMGetNextInstruction, self.ptr, Instruction)


#===----------------------------------------------------------------------===
# Builder
#===----------------------------------------------------------------------===

        
class Builder(object):

    @staticmethod
    def new():
        return Builder(_core.LLVMCreateBuilder())
        
    def __init__(self, ptr):
        self.ptr = ptr

    def __del__(self):
        _core.LLVMDisposeBuilder(self.ptr)

    def position(self, block, instr=None):
        if instr:
            _core.LLVMPositionBuilder(self.ptr, block.ptr, instr.ptr)
        else:
            _core.LLVMPositionBuilder(self.ptr, block.ptr)

    def position_before(self, instr):
        _core.LLVMPositionBuilderBefore(self.ptr, instr.ptr)
        
    def position_at_end(self, bblk):
        _core.LLVMPositionBuilderAtEnd(self.ptr, bblk.ptr)

    @property
    def insert_block(self):
        return BasicBlock(_core.LLVMGetInsertBlock(self.ptr))

    def ret_void(self):
        return Instruction(_core.LLVMBuildRetVoid(self.ptr))
        
    def ret(self, value):
        _check_is_value(value)
        return Instruction(_core.LLVMBuildRet(self.ptr, value.ptr))
        
    def branch(self, bblk):
        _check_is_basic_block(bblk)
        return Instruction(_core.LLVMBuildBr(self.ptr, bblk.ptr))
        
    def cbranch(self, if_value, then_blk, else_blk):
        _check_is_value(if_value)
        _check_is_basic_block(then_blk)
        _check_is_basic_block(else_blk)
        return Instruction(_core.LLVMBuildCondBr(self.ptr, if_value.ptr, then_blk.ptr, else_blk.ptr))
        
    def switch(self, value, else_blk, n=10):
        _check_is_value(value)
        _check_is_basic_block(else_blk)
        return SwitchInstruction(_core.LLVMBuildSwitch(self.ptr, value.ptr, else_blk.ptr, n))
        
    def invoke(self, func, args, then_blk, catch_blk, name=""):
        _check_is_function(func)
        _check_is_basic_block(then_blk)
        _check_is_basic_block(catch_blk)
        args2 = _unpack_values(args)
        return CallOrInvokeInstruction(_core.LLVMBuildInvoke(self.ptr, func.ptr, args2, then_blk.ptr, catch_blk.ptr, name))

    def unwind(self):
        return Instruction(_core.LLVMBuildUnwind(self.ptr))
        
    def unreachable(self):
        return Instruction(_core.LLVMBuildUnreachable(self.ptr))

    # arithmethic-related
    
    def add(self, lhs, rhs, name=""):
        _check_is_value(lhs)
        _check_is_value(rhs)
        return Value(_core.LLVMBuildAdd(self.ptr, lhs.ptr, rhs.ptr, name))
        
    def sub(self, lhs, rhs, name=""):
        _check_is_value(lhs)
        _check_is_value(rhs)
        return Value(_core.LLVMBuildSub(self.ptr, lhs.ptr, rhs.ptr, name))

    def mul(self, lhs, rhs, name=""):
        _check_is_value(lhs)
        _check_is_value(rhs)
        return Value(_core.LLVMBuildMul(self.ptr, lhs.ptr, rhs.ptr, name))

    def udiv(self, lhs, rhs, name=""):
        _check_is_value(lhs)
        _check_is_value(rhs)
        return Value(_core.LLVMBuildUDiv(self.ptr, lhs.ptr, rhs.ptr, name))

    def sdiv(self, lhs, rhs, name=""):
        _check_is_value(lhs)
        _check_is_value(rhs)
        return Value(_core.LLVMBuildSDiv(self.ptr, lhs.ptr, rhs.ptr, name))

    def fdiv(self, lhs, rhs, name=""):
        _check_is_value(lhs)
        _check_is_value(rhs)
        return Value(_core.LLVMBuildFDiv(self.ptr, lhs.ptr, rhs.ptr, name))

    def urem(self, lhs, rhs, name=""):
        _check_is_value(lhs)
        _check_is_value(rhs)
        return Value(_core.LLVMBuildURem(self.ptr, lhs.ptr, rhs.ptr, name))

    def srem(self, lhs, rhs, name=""):
        _check_is_value(lhs)
        _check_is_value(rhs)
        return Value(_core.LLVMBuildSRem(self.ptr, lhs.ptr, rhs.ptr, name))

    def frem(self, lhs, rhs, name=""):
        _check_is_value(lhs)
        _check_is_value(rhs)
        return Value(_core.LLVMBuildFRem(self.ptr, lhs.ptr, rhs.ptr, name))

    def shl(self, lhs, rhs, name=""):
        _check_is_value(lhs)
        _check_is_value(rhs)
        return Value(_core.LLVMBuildShl(self.ptr, lhs.ptr, rhs.ptr, name))

    def lshr(self, lhs, rhs, name=""):
        _check_is_value(lhs)
        _check_is_value(rhs)
        return Value(_core.LLVMBuildLShr(self.ptr, lhs.ptr, rhs.ptr, name))

    def ashr(self, lhs, rhs, name=""):
        _check_is_value(lhs)
        _check_is_value(rhs)
        return Value(_core.LLVMBuildAShr(self.ptr, lhs.ptr, rhs.ptr, name))

    def and_(self, lhs, rhs, name=""):
        _check_is_value(lhs)
        _check_is_value(rhs)
        return Value(_core.LLVMBuildAnd(self.ptr, lhs.ptr, rhs.ptr, name))

    def or_(self, lhs, rhs, name=""):
        _check_is_value(lhs)
        _check_is_value(rhs)
        return Value(_core.LLVMBuildOr(self.ptr, lhs.ptr, rhs.ptr, name))

    def xor(self, lhs, rhs, name=""):
        _check_is_value(lhs)
        _check_is_value(rhs)
        return Value(_core.LLVMBuildXor(self.ptr, lhs.ptr, rhs.ptr, name))

    def neg(self, val, name=""):
        _check_is_value(val)
        return Instruction(_core.LLVMBuildNeg(self.ptr, val.ptr, name))

    def not_(self, val, name=""):
        _check_is_value(val)
        return Instruction(_core.LLVMBuildNot(self.ptr, val.ptr, name))

    # memory

    def malloc(self, ty, name=""):
        _check_is_type(ty)
        return Instruction(_core.LLVMBuildMalloc(self.ptr, ty.ptr, name))

    def malloc_array(self, ty, size, name=""):
        _check_is_type(ty)
        _check_is_value(size)
        return Instruction(_core.LLVMBuildArrayMalloc(self.ptr, ty.ptr, size.ptr, name))

    def alloca(self, ty, name=""):
        _check_is_type(ty)
        return Instruction(_core.LLVMBuildAlloc(self.ptr, ty.ptr, name))

    def alloca_array(self, ty, size, name=""):
        _check_is_type(ty)
        _check_is_value(size)
        return Instruction(_core.LLVMBuildArrayAlloca(self.ptr, ty.ptr, size.ptr, name))

    def free(self, ptr):
        _check_is_pointer(ptr)
        return Instruction(_core.LLVMBuildFree(self.ptr, ptr.ptr))

    def load(self, ptr, name=""):
        _check_is_pointer(ptr)
        return Instruction(_core.LLVMBuildLoad(self.ptr, ptr.ptr, name))

    def store(self, value, ptr):
        _check_is_value(value)
        _check_is_pointer(ptr)
        return Instruction(_core.LLVMBuildStore(self.ptr, value.ptr, ptr.ptr))

    def gep(self, ptr, indices, name=""):
        _check_is_pointer(ptr)
        index_ptrs = _unpack_values(indices)
        return Value(_core.LLVMBuildGEP(self.ptr, ptr.ptr, index_ptrs, name))

    # casts

    def trunc(self, value, dest_ty, name=""):
        _check_is_value(value)
        _check_is_type(dest_ty)
        return Value(_core.LLVMBuildTrunc(self.ptr, value.ptr, dest_ty.ptr, name))

    def zext(self, value, dest_ty, name=""):
        _check_is_value(value)
        _check_is_type(dest_ty)
        return Value(_core.LLVMBuildZExt(self.ptr, value.ptr, dest_ty.ptr, name))

    def sext(self, value, dest_ty, name=""):
        _check_is_value(value)
        _check_is_type(dest_ty)
        return Value(_core.LLVMBuildSExt(self.ptr, value.ptr, dest_ty.ptr, name))

    def fptoui(self, value, dest_ty, name=""):
        _check_is_value(value)
        _check_is_type(dest_ty)
        return Value(_core.LLVMBuildFPToUI(self.ptr, value.ptr, dest_ty.ptr, name))

    def fptosi(self, value, dest_ty, name=""):
        _check_is_value(value)
        _check_is_type(dest_ty)
        return Value(_core.LLVMBuildFPToSI(self.ptr, value.ptr, dest_ty.ptr, name))

    def uitofp(self, value, dest_ty, name=""):
        _check_is_value(value)
        _check_is_type(dest_ty)
        return Value(_core.LLVMBuildUIToFP(self.ptr, value.ptr, dest_ty.ptr, name))

    def sitofp(self, value, dest_ty, name=""):
        _check_is_value(value)
        _check_is_type(dest_ty)
        return Value(_core.LLVMBuildSIToFP(self.ptr, value.ptr, dest_ty.ptr, name))

    def fptrunc(self, value, dest_ty, name=""):
        _check_is_value(value)
        _check_is_type(dest_ty)
        return Value(_core.LLVMBuildFPTrunc(self.ptr, value.ptr, dest_ty.ptr, name))

    def fpext(self, value, dest_ty, name=""):
        _check_is_value(value)
        _check_is_type(dest_ty)
        return Value(_core.LLVMBuildFPExt(self.ptr, value.ptr, dest_ty.ptr, name))

    def ptrtoint(self, value, dest_ty, name=""):
        _check_is_value(value)
        _check_is_type(dest_ty)
        return Value(_core.LLVMBuildPtrToInt(self.ptr, value.ptr, dest_ty.ptr, name))

    def inttoptr(self, value, dest_ty, name=""):
        _check_is_value(value)
        _check_is_type(dest_ty)
        return Value(_core.LLVMBuildIntToPtr(self.ptr, value.ptr, dest_ty.ptr, name))

    def bitcast(self, value, dest_ty, name=""):
        _check_is_value(value)
        _check_is_type(dest_ty)
        return Value(_core.LLVMBuildBitCast(self.ptr, value.ptr, dest_ty.ptr, name))

    # comparisons

    def icmp(self, ipred, lhs, rhs, name=""):
        _check_is_value(lhs)
        _check_is_value(rhs)
        return Value(_core.LLVMBuildICmp(self.ptr, ipred, lhs.ptr, rhs.ptr, name))
        
    def fcmp(self, rpred, lhs, rhs, name=""):
        _check_is_value(lhs)
        _check_is_value(rhs)
        return Value(_core.LLVMBuildFCmp(self.ptr, rpred, lhs.ptr, rhs.ptr, name))

    # misc

    def phi(self, ty, name=""):
        _check_is_type(ty)
        return PHINode(_core.LLVMBuildPhi(self.ptr, ty.ptr, name))
        
    def call(self, fn, args, name=""):
        _check_is_function(fn)
        arg_ptrs = _unpack_values(args)
        return CallOrInvokeInstruction(_core.LLVMBuildCall(self.ptr, fn.ptr, arg_ptrs, name))
        
    def select(self, if_blk, then_blk, else_blk, name=""):
        _check_is_basic_block(if_blk)
        _check_is_basic_block(then_blk)
        _check_is_basic_block(else_blk)
        return Value(_core.LLVMBuildSelect(self.ptr, if_blk.ptr, then_blk.ptr, else_blk.ptr, name))
    
    def vaarg(self, list_val, ty, name=""):
        _check_is_value(list_val)
        _check_is_type(ty)
        return Instruction(_core.LLVMBuildVAArg(self.ptr, list_val.ptr, ty.ptr, name))
    
    def extract_element(self, vec_val, idx_val, name=""):
        _check_is_value(vec_val)
        _check_is_value(idx_val)
        return Value(_core.LLVMBuildExtractElement(self.ptr, vec_val.ptr, idx_val.ptr, name))
    
    def insert_element(self, vec_val, elt_val, idx_val, name=""):
        _check_is_value(vec_val)
        _check_is_value(elt_val)
        _check_is_value(idx_val)
        return Value(_core.LLVMBuildInsertElement(self.ptr, vec_val.ptr, elt_val.ptr, idx_val.ptr, name))

    def shuffle_vector(self, vecA, vecB, mask, name=""):
        _check_is_value(vecA)
        _check_is_value(vecB)
        _check_is_value(mask)
        return Value(_core.LLVMBuildShuffleVector(self.ptr, vecA.ptr, vecB.ptr, mask.ptr, name))


#===----------------------------------------------------------------------===
# Module provider
#===----------------------------------------------------------------------===

        
class ModuleProvider(object):

    @staticmethod
    def new(module):
        mp = ModuleProvider(_core.LLVMCreateModuleProviderForExistingModule(module.ptr))
        module._own(mp)
        return mp

    def __init__(self, ptr):
        self.ptr = ptr

    def __del__(self):
        _core.LLVMDisposeModuleProvider(self.ptr)


#===----------------------------------------------------------------------===
# Memory buffer
#===----------------------------------------------------------------------===


class MemoryBuffer(object):

    @staticmethod
    def from_file(self, fname):
        ret = _core.LLVMCreateMemoryBufferWithContentsOfFile(fname)
        if isinstance(ret, str):
            return (None, ret)
        else:
            obj = MemoryBuffer(ret)
            return (obj, "")

    @staticmethod
    def from_stdin(self):
        ret = _core.LLVMCreateMemoryBufferWithSTDIN()
        if isinstance(ret, str):
            return (None, ret)
        else:
            obj = MemoryBuffer(ret)
            return (obj, "")

    def __init__(self, ptr):
        self.ptr = ptr

    def __del__(self):
        _core.LLVMDisposeMemoryBuffer(self.ptr)


#===----------------------------------------------------------------------===
# Pass manager
#===----------------------------------------------------------------------===

class PassManager(object):

    @staticmethod
    def new():
        return PassManager(_core.LLVMCreatePassManager())

    def __init__(self, ptr):
        self.ptr = ptr

    def __del__(self):
        _core.LLVMDisposePassManager(self.ptr)

    def run(self, module):
        _check_is_module(module)
        return _core.LLVMRunPassManager(self.ptr, module.ptr)


class FunctionPassManager(PassManager):

    @staticmethod
    def new(mp):
        _check_is_module_provider(mp)
        return FunctionPassManager(_core.LLVMCreateFunctionPassManager(mp.ptr))

    def __init__(self, ptr):
        PassManager.__init__(self, ptr)

    def __del__(self):
        PassManager.__del__(self)

    def initialize(self):
        _core.LLVMInitializeFunctionPassManager(self.ptr)

    def run(self, fn):
        _check_is_function(fn)
        return _core.LLVMRunFunctionPassManager(fn.ptr)

    def finalize(self):
        _core.LLVMFinalizeFunctionPassManager(self.ptr)

