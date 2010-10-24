#
# Copyright (c) 2008-10, Mahadevan R All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#  * Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
#  * Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
#  * Neither the name of this software, nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

"""Core classes of LLVM.

The llvm.core module contains classes and constants required to build the
in-memory intermediate representation (IR) data structures."""


import llvm                 # top-level, for common stuff
import llvm._core as _core  # C wrappers
import llvm._util as _util  # utility functions


#===----------------------------------------------------------------------===
# Enumerations
#===----------------------------------------------------------------------===

# type kinds (LLVMTypeKind enum)
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
TYPE_METADATA   = 14

# value IDs (llvm::Value::ValueTy enum)
VALUE_ARGUMENT                          = 0
VALUE_BASIC_BLOCK                       = 1
VALUE_FUNCTION                          = 2
VALUE_GLOBAL_ALIAS                      = 3
VALUE_GLOBAL_VARIABLE                   = 4
VALUE_UNDEF_VALUE                       = 5
VALUE_BLOCK_ADDRESS                     = 6
VALUE_CONSTANT_EXPR                     = 7
VALUE_CONSTANT_AGGREGATE_ZERO           = 8
VALUE_CONSTANT_INT                      = 9
VALUE_CONSTANT_FP                       = 10
VALUE_CONSTANT_ARRAY                    = 11
VALUE_CONSTANT_STRUCT                   = 12
VALUE_CONSTANT_VECTOR                   = 13
VALUE_CONSTANT_POINTER_NULL             = 14
VALUE_MD_NODE                           = 15
VALUE_MD_STRING                         = 16
VALUE_INLINE_ASM                        = 17
VALUE_PSEUDO_SOURCE_VALUE               = 18
VALUE_FIXED_STACK_PSEUDO_SOURCE_VALUE   = 19
VALUE_INSTRUCTION                       = 20

# instruction opcodes (from include/llvm/Instruction.def)
OPCODE_RET            = 1
OPCODE_BR             = 2
OPCODE_SWITCH         = 3
OPCODE_INDIRECT_BR    = 4
OPCODE_INVOKE         = 5
OPCODE_UNWIND         = 6
OPCODE_UNREACHABLE    = 7
OPCODE_ADD            = 8
OPCODE_FADD           = 9
OPCODE_SUB            = 10
OPCODE_FSUB           = 11
OPCODE_MUL            = 12
OPCODE_FMUL           = 13
OPCODE_UDIV           = 14
OPCODE_SDIV           = 15
OPCODE_FDIV           = 16
OPCODE_UREM           = 17
OPCODE_SREM           = 18
OPCODE_FREM           = 19
OPCODE_SHL            = 20
OPCODE_LSHR           = 21
OPCODE_ASHR           = 22
OPCODE_AND            = 23
OPCODE_OR             = 24
OPCODE_XOR            = 25
OPCODE_ALLOCA         = 26
OPCODE_LOAD           = 27
OPCODE_STORE          = 28
OPCODE_GETELEMENTPTR  = 29
OPCODE_TRUNC          = 30
OPCODE_ZEXT           = 31
OPCODE_SEXT           = 32
OPCODE_FPTOUI         = 33
OPCODE_FPTOSI         = 34
OPCODE_UITOFP         = 35
OPCODE_SITOFP         = 36
OPCODE_FPTRUNC        = 37
OPCODE_FPEXT          = 38
OPCODE_PTRTOINT       = 39
OPCODE_INTTOPTR       = 40
OPCODE_BITCAST        = 41
OPCODE_ICMP           = 42
OPCODE_FCMP           = 43
OPCODE_PHI            = 44
OPCODE_CALL           = 45
OPCODE_SELECT         = 46
OPCODE_USEROP1        = 47
OPCODE_USEROP2        = 48
OPCODE_VAARG          = 49
OPCODE_EXTRACTELEMENT = 50
OPCODE_INSERTELEMENT  = 51
OPCODE_SHUFFLEVECTOR  = 52
OPCODE_EXTRACTVALUE   = 53
OPCODE_INSERTVALUE    = 54

# calling conventions
CC_C            = 0
CC_FASTCALL     = 8
CC_COLDCALL     = 9
CC_X86_STDCALL  = 64
CC_X86_FASTCALL = 65

# int predicates
ICMP_EQ         = 32
ICMP_NE         = 33
ICMP_UGT        = 34
ICMP_UGE        = 35
ICMP_ULT        = 36
ICMP_ULE        = 37
ICMP_SGT        = 38
ICMP_SGE        = 39
ICMP_SLT        = 40
ICMP_SLE        = 41

# same as ICMP_xx, for backward compatibility
IPRED_EQ        = ICMP_EQ
IPRED_NE        = ICMP_NE
IPRED_UGT       = ICMP_UGT
IPRED_UGE       = ICMP_UGE
IPRED_ULT       = ICMP_ULT
IPRED_ULE       = ICMP_ULE
IPRED_SGT       = ICMP_SGT
IPRED_SGE       = ICMP_SGE
IPRED_SLT       = ICMP_SLT
IPRED_SLE       = ICMP_SLE

# real predicates
FCMP_FALSE      = 0
FCMP_OEQ        = 1
FCMP_OGT        = 2
FCMP_OGE        = 3
FCMP_OLT        = 4
FCMP_OLE        = 5
FCMP_ONE        = 6
FCMP_ORD        = 7
FCMP_UNO        = 8
FCMP_UEQ        = 9
FCMP_UGT        = 10
FCMP_UGE        = 11
FCMP_ULT        = 12
FCMP_ULE        = 13
FCMP_UNE        = 14
FCMP_TRUE       = 15

# real predicates
RPRED_FALSE     = FCMP_FALSE
RPRED_OEQ       = FCMP_OEQ
RPRED_OGT       = FCMP_OGT
RPRED_OGE       = FCMP_OGE
RPRED_OLT       = FCMP_OLT
RPRED_OLE       = FCMP_OLE
RPRED_ONE       = FCMP_ONE
RPRED_ORD       = FCMP_ORD
RPRED_UNO       = FCMP_UNO
RPRED_UEQ       = FCMP_UEQ
RPRED_UGT       = FCMP_UGT
RPRED_UGE       = FCMP_UGE
RPRED_ULT       = FCMP_ULT
RPRED_ULE       = FCMP_ULE
RPRED_UNE       = FCMP_UNE
RPRED_TRUE      = FCMP_TRUE

# linkages (see llvm-c/Core.h)
LINKAGE_EXTERNAL                        = 0
LINKAGE_AVAILABLE_EXTERNALLY            = 1
LINKAGE_LINKONCE_ANY                    = 2
LINKAGE_LINKONCE_ODR                    = 3
LINKAGE_WEAK_ANY                        = 4
LINKAGE_WEAK_ODR                        = 5
LINKAGE_APPENDING                       = 6
LINKAGE_INTERNAL                        = 7
LINKAGE_PRIVATE                         = 8
LINKAGE_DLLIMPORT                       = 9
LINKAGE_DLLEXPORT                       = 10
LINKAGE_EXTERNAL_WEAK                   = 11
LINKAGE_GHOST                           = 12
LINKAGE_COMMON                          = 13
LINKAGE_LINKER_PRIVATE                  = 14
LINKAGE_LINKER_PRIVATE_WEAK             = 15
LINKAGE_LINKER_PRIVATE_WEAK_DEF_AUTO    = 16

# visibility (see llvm/GlobalValue.h)
VISIBILITY_DEFAULT   = 0
VISIBILITY_HIDDEN    = 1
VISIBILITY_PROTECTED = 2

# parameter attributes (see llvm/Attributes.h)
ATTR_NONE               = 0
ATTR_ZEXT               = 1
ATTR_SEXT               = 2
ATTR_NO_RETURN          = 4
ATTR_IN_REG             = 8
ATTR_STRUCT_RET         = 16
ATTR_NO_UNWIND          = 32
ATTR_NO_ALIAS           = 64
ATTR_BY_VAL             = 128
ATTR_NEST               = 256
ATTR_READ_NONE          = 512
ATTR_READONLY           = 1024
ATTR_NO_INLINE          = 1<<11
ATTR_ALWAYS_INLINE      = 1<<12
ATTR_OPTIMIZE_FOR_SIZE  = 1<<13
ATTR_STACK_PROTECT      = 1<<14
ATTR_STACK_PROTECT_REQ  = 1<<15
ATTR_NO_CAPTURE         = 1<<21
ATTR_NO_REDZONE         = 1<<22
ATTR_NO_IMPLICIT_FLOAT  = 1<<23
ATTR_NAKED              = 1<<24
ATTR_INLINE_HINT        = 1<<25

# intrinsic IDs
from llvm._intrinsic_ids import *


#===----------------------------------------------------------------------===
# Helpers (for internal use)
#===----------------------------------------------------------------------===

def check_is_type(obj):         _util.check_gen(obj, Type)
def check_is_type_struct(obj):  _util.check_gen(obj, StructType)
def check_is_value(obj):        _util.check_gen(obj, Value)
def check_is_constant(obj):     _util.check_gen(obj, Constant)
def check_is_function(obj):     _util.check_gen(obj, Function)
def check_is_basic_block(obj):  _util.check_gen(obj, BasicBlock)
def check_is_module(obj):       _util.check_gen(obj, Module)

def unpack_types(objlst):     return _util.unpack_gen(objlst, check_is_type)
def unpack_values(objlst):    return _util.unpack_gen(objlst, check_is_value)
def unpack_constants(objlst): return _util.unpack_gen(objlst, check_is_constant)

def check_is_callable(obj):
    if isinstance(obj, Function):
        return
    typ = obj.type
    if isinstance(typ, PointerType) and \
        isinstance(typ.pointee, FunctionType):
        return
    raise TypeError, "argument is neither a function nor a function pointer"

def _to_int(v):
    if v:
        return 1
    else:
        return 0


#===----------------------------------------------------------------------===
# Module
#===----------------------------------------------------------------------===

class Module(llvm.Ownable, llvm.Cacheable):
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

    @staticmethod
    def from_bitcode(fileobj):
        """Create a Module instance from the contents of a bitcode
        file."""

        data = fileobj.read()
        ret = _core.LLVMGetModuleFromBitcode(data)
        if not ret:
            raise llvm.LLVMException, "Unable to create module from bitcode"
        elif isinstance(ret, str):
            raise llvm.LLVMException, ret
        else:
            return Module(ret)

    @staticmethod
    def from_assembly(fileobj):
        """Create a Module instance from the contents of an LLVM
        assembly (.ll) file."""

        data = fileobj.read()
        ret = _core.LLVMGetModuleFromAssembly(data)
        if not ret:
            raise llvm.LLVMException, \
                "Unable to create module from assembly"
        elif isinstance(ret, str):
            raise llvm.LLVMException, ret
        else:
            return Module(ret)

    def __init__(self, ptr):
        """DO NOT CALL DIRECTLY.

        Use the static method `Module.new' instead.
        """
        llvm.Ownable.__init__(self, ptr, _core.LLVMDisposeModule)

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

    def __ne__(self, rhs):
        return not self == rhs

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

    @property
    def pointer_size(self):
        """Pointer size of target platform.

        Can be 0, 32 or 64. Zero represents
        llvm::Module::AnyPointerSize."""
        return _core.LLVMModuleGetPointerSize(self.ptr)

    def link_in(self, other):
        """Link the `other' module into this one.

        The `other' module is linked into this one such that types,
        global variables, function, etc. are matched and resolved.

        The `other' module is no longer valid after this method is
        invoked, all refs to it should be dropped.

        In the future, this API might be replaced with a full-fledged
        Linker class.
        """
        check_is_module(other)
        other.forget() # remove it from object cache
        ret = _core.LLVMLinkModules(self.ptr, other.ptr)
        if isinstance(ret, str):
            raise llvm.LLVMException, ret
        # Do not try to destroy the other module's llvm::Module*.
        other._own(llvm.DummyOwner())

    def add_type_name(self, name, ty):
        """Map a string to a type.

        Similar to C's struct/typedef declarations. Returns True
        if entry already existed (in which case nothing is changed),
        False otherwise.
        """
        check_is_type(ty)
        return _core.LLVMAddTypeName(self.ptr, name, ty.ptr) != 0

    def delete_type_name(self, name):
        """Removes a named type.

        Undoes what add_type_name() does.
        """
        _core.LLVMDeleteTypeName(self.ptr, name)

    def get_type_named(self, name):
        """Return a Type object with the given name."""
        ptr  = _core.LLVMGetTypeByName(self.ptr, name)
        if ptr:
            kind = _core.LLVMGetTypeKind(ptr)
            return _make_type(ptr, kind)
        return None

    def add_global_variable(self, ty, name):
        """Add a global variable of given type with given name."""
        return GlobalVariable.new(self, ty, name)

    def get_global_variable_named(self, name):
        """Return a GlobalVariable object for the given name."""
        return GlobalVariable.get(self, name)

    @property
    def global_variables(self):
        """All global variables in this module."""
        return _util.wrapiter(_core.LLVMGetFirstGlobal,
            _core.LLVMGetNextGlobal, self.ptr, _make_value)

    def add_function(self, ty, name):
        """Add a function of given type with given name."""
        return Function.new(self, ty, name)

    def get_function_named(self, name):
        """Return a Function object representing function with given name."""
        return Function.get(self, name)

    def get_or_insert_function(self, ty, name):
        """Like get_function_named(), but does add_function() first, if
        function is not present."""
        return Function.get_or_insert(self, ty, name)

    @property
    def functions(self):
        """All functions in this module."""
        return _util.wrapiter(_core.LLVMGetFirstFunction,
            _core.LLVMGetNextFunction, self.ptr, _make_value)

    def verify(self):
        """Verify module.

        Checks module for errors. Raises `llvm.LLVMException' on any
        error."""
        ret = _core.LLVMVerifyModule(self.ptr)
        if ret != "":
            raise llvm.LLVMException, ret

    def to_bitcode(self, fileobj):
        """Write bitcode representation of module to given file-like
        object."""

        data = _core.LLVMGetBitcodeFromModule(self.ptr)
        if not data:
            raise llvm.LLVMException, "Unable to create bitcode"
        fileobj.write(data)


#===----------------------------------------------------------------------===
# Types
#===----------------------------------------------------------------------===

class Type(object):
    """Represents a type, like a 32-bit integer or an 80-bit x86 float.

    Use one of the static methods to create an instance. Example:
      ty = Type.double()
    """

    @staticmethod
    def int(bits=32):
        """Create an integer type having the given bit width."""
        if bits == 1:
            return _make_type(_core.LLVMInt1Type(), TYPE_INTEGER)
        elif bits == 8:
            return _make_type(_core.LLVMInt8Type(), TYPE_INTEGER)
        elif bits == 16:
            return _make_type(_core.LLVMInt16Type(), TYPE_INTEGER)
        elif bits == 32:
            return _make_type(_core.LLVMInt32Type(), TYPE_INTEGER)
        elif bits == 64:
            return _make_type(_core.LLVMInt64Type(), TYPE_INTEGER)
        else:
            bits = int(bits) # bits must be an int
            return _make_type(_core.LLVMIntType(bits), TYPE_INTEGER)

    @staticmethod
    def float():
        """Create a 32-bit floating point type."""
        return _make_type(_core.LLVMFloatType(), TYPE_FLOAT)

    @staticmethod
    def double():
        """Create a 64-bit floating point type."""
        return _make_type(_core.LLVMDoubleType(), TYPE_DOUBLE)

    @staticmethod
    def x86_fp80():
        """Create a 80-bit x86 floating point type."""
        return _make_type(_core.LLVMX86FP80Type(), TYPE_X86_FP80)

    @staticmethod
    def fp128():
        """Create a 128-bit floating point type (with 112-bit
        mantissa)."""
        return _make_type(_core.LLVMFP128Type(), TYPE_FP128)

    @staticmethod
    def ppc_fp128():
        """Create a 128-bit floating point type (two 64-bits)."""
        return _make_type(_core.LLVMPPCFP128Type(), TYPE_PPC_FP128)

    @staticmethod
    def function(return_ty, param_tys, var_arg=False):
        """Create a function type.

        Creates a function type that returns a value of type
        `return_ty', takes arguments of types as given in the iterable
        `param_tys'. Set `var_arg' to True (default is False) for a
        variadic function."""
        check_is_type(return_ty)
        var_arg = _to_int(var_arg) # ensure int
        params = unpack_types(param_tys)
        return _make_type(_core.LLVMFunctionType(return_ty.ptr, params,
                    var_arg), TYPE_FUNCTION)

    @staticmethod
    def struct(element_tys): # not packed
        """Create a (unpacked) structure type.

        Creates a structure type with elements of types as given in the
        iterable `element_tys'. This method creates a unpacked
        structure. For a packed one, use the packed_struct() method."""
        elems = unpack_types(element_tys)
        return _make_type(_core.LLVMStructType(elems, 0), TYPE_STRUCT)

    @staticmethod
    def packed_struct(element_tys):
        """Create a (packed) structure type.

        Creates a structure type with elements of types as given in the
        iterable `element_tys'. This method creates a packed
        structure. For an unpacked one, use the struct() method."""
        elems = unpack_types(element_tys)
        return _make_type(_core.LLVMStructType(elems, 1), TYPE_STRUCT)

    @staticmethod
    def array(element_ty, count):
        """Create an array type.

        Creates a type for an array of elements of type `element_ty',
        having 'count' elements."""
        check_is_type(element_ty)
        count = int(count) # must be an int
        return _make_type(_core.LLVMArrayType(element_ty.ptr, count),
                    TYPE_ARRAY)

    @staticmethod
    def pointer(pointee_ty, addr_space=0):
        """Create a pointer type.

        Creates a pointer type, which can point to values of type
        `pointee_ty', in the address space `addr_space'."""
        check_is_type(pointee_ty)
        addr_space = int(addr_space) # must be an int
        return _make_type(_core.LLVMPointerType(pointee_ty.ptr,
                    addr_space), TYPE_POINTER)

    @staticmethod
    def vector(element_ty, count):
        """Create a vector type.

        Creates a type for a vector of elements of type `element_ty',
        having `count' elements."""
        check_is_type(element_ty)
        count = int(count) # must be an int
        return _make_type(_core.LLVMVectorType(element_ty.ptr, count),
                    TYPE_VECTOR)

    @staticmethod
    def void():
        """Create a void type.

        Represents the `void' type."""
        return _make_type(_core.LLVMVoidType(), TYPE_VOID)

    @staticmethod
    def label():
        """Create a label type."""
        return _make_type(_core.LLVMLabelType(), TYPE_LABEL)

    @staticmethod
    def opaque():
        """Create an opaque type.

        Opaque types are used to create self-referencing types."""
        return _make_type(_core.LLVMOpaqueType(), TYPE_OPAQUE)

    def __init__(self, ptr, kind):
        """DO NOT CALL DIRECTLY.

        Use one of the static methods instead."""
        self.ptr = ptr
        self.kind = kind
        """An enum (int) value denoting which type this is.

        Use the symbolic constants TYPE_* defined in llvm.core
        module."""

    def __str__(self):
        """Text representation of a type.

        Returns the textual representation (`llvm assembly') of the type."""
        return _core.LLVMDumpTypeToString(self.ptr)

    def __eq__(self, rhs):
        if isinstance(rhs, Type):
            return str(self) == str(rhs)
        else:
            return False

    def __ne__(self, rhs):
        return not self == rhs

    def refine(self, dest):
        """Refine the abstract type represented by self into a concrete class.

        This object is no longer valid after refining, so do not hold
        references to it after calling. See the user guide for examples on how
        to use this."""

        check_is_type(dest)
        _core.LLVMRefineType(self.ptr, dest.ptr)
        self.ptr = None


class IntegerType(Type):
    """Represents an integer type."""

    @property
    def width(self):
        """The width of the integer type, in bits."""
        return _core.LLVMGetIntTypeWidth(self.ptr)


class FunctionType(Type):
    """Represents a function type."""

    @property
    def return_type(self):
        """The type of the value returned by this function."""
        ptr  = _core.LLVMGetReturnType(self.ptr)
        kind = _core.LLVMGetTypeKind(ptr)
        return _make_type(ptr, kind)

    @property
    def vararg(self):
        """True if this function is variadic."""
        return _core.LLVMIsFunctionVarArg(self.ptr) != 0

    @property
    def args(self):
        """An iterable that yields Type objects, representing the types of the
        arguments accepted by this function, in order."""
        pp = _core.LLVMGetFunctionTypeParams(self.ptr)
        return [ _make_type(p, _core.LLVMGetTypeKind(p)) for p in pp ]

    @property
    def arg_count(self):
        """Number of arguments accepted by this function.

        Same as len(obj.args), but faster."""
        return _core.LLVMCountParamTypes(self.ptr)


class StructType(Type):
    """Represents a structure type."""

    @property
    def element_count(self):
        """Number of elements (members) in the structure.

        Same as len(obj.elements), but faster."""
        return _core.LLVMCountStructElementTypes(self.ptr)

    @property
    def elements(self):
        """An iterable that yieldsd Type objects, representing the types of the
        elements (members) of the structure, in order."""
        pp = _core.LLVMGetStructElementTypes(self.ptr)
        return [ _make_type(p, _core.LLVMGetTypeKind(p)) for p in pp ]

    @property
    def packed(self):
        """True if the structure is packed, False otherwise."""
        return _core.LLVMIsPackedStruct(self.ptr) != 0


class ArrayType(Type):
    """Represents an array type."""

    @property
    def element(self):
        ptr  = _core.LLVMGetElementType(self.ptr)
        kind = _core.LLVMGetTypeKind(ptr)
        return _make_type(ptr, kind)

    @property
    def count(self):
        return _core.LLVMGetArrayLength(self.ptr)


class PointerType(Type):

    @property
    def pointee(self):
        ptr = _core.LLVMGetElementType(self.ptr)
        kind = _core.LLVMGetTypeKind(ptr)
        return _make_type(ptr, kind)

    @property
    def address_space(self):
        return _core.LLVMGetPointerAddressSpace(self.ptr)


class VectorType(Type):

    @property
    def element(self):
        ptr  = _core.LLVMGetElementType(self.ptr)
        kind = _core.LLVMGetTypeKind(ptr)
        return _make_type(ptr, kind)

    @property
    def count(self):
        return _core.LLVMGetVectorSize(self.ptr)


#===----------------------------------------------------------------------===
# Type factory method
#===----------------------------------------------------------------------===

# type ID -> class map
__class_for_typeid = {
    TYPE_INTEGER     : IntegerType,
    TYPE_FUNCTION    : FunctionType,
    TYPE_STRUCT      : StructType,
    TYPE_ARRAY       : ArrayType,
    TYPE_POINTER     : PointerType,
    TYPE_VECTOR      : VectorType,
}

def _make_type(ptr, kind):
    class_obj = __class_for_typeid.get(kind)
    if class_obj:
        return class_obj(ptr, kind)
    else:
        # "generic" type
        return Type(ptr, kind)


#===----------------------------------------------------------------------===
# Type Handle
#===----------------------------------------------------------------------===

class TypeHandle(object):

    @staticmethod
    def new(abstract_ty):
        check_is_type(abstract_ty)
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

class Value(llvm.Cacheable):

    def __init__(self, ptr):
        self.ptr = ptr

    def __str__(self):
        return _core.LLVMDumpValueToString(self.ptr)

    def __eq__(self, rhs):
        if isinstance(rhs, Value):
            return str(self) == str(rhs)
        else:
            return False

    def __ne__(self, rhs):
        return not self == rhs

    def _get_name(self):
        return _core.LLVMGetValueName(self.ptr)

    def _set_name(self, value):
        return _core.LLVMSetValueName(self.ptr, value)

    name = property(_get_name, _set_name)

    @property
    def value_id(self):
        return _core.LLVMValueGetID(self.ptr)

    @property
    def type(self):
        ptr  = _core.LLVMTypeOf(self.ptr)
        kind = _core.LLVMGetTypeKind(ptr)
        return _make_type(ptr, kind)

    @property
    def use_count(self):
        return _core.LLVMValueGetNumUses(self.ptr)

    @property
    def uses(self):
        return [ _make_value(v) for v in _core.LLVMValueGetUses(self.ptr) ]


class User(Value):

    @property
    def operand_count(self):
        return _core.LLVMUserGetNumOperands(self.ptr)

    @property
    def operands(self):
        """Yields operands of this instruction."""
        return [self._get_operand(i) for i in range(self.operand_count)]

    def _get_operand(self, i):
        return _make_value(_core.LLVMUserGetOperand(self.ptr, i))


class Constant(User):

    @staticmethod
    def null(ty):
        check_is_type(ty)
        return _make_value(_core.LLVMConstNull(ty.ptr))

    @staticmethod
    def all_ones(ty):
        check_is_type(ty)
        return _make_value(_core.LLVMConstAllOnes(ty.ptr))

    @staticmethod
    def undef(ty):
        check_is_type(ty)
        return _make_value(_core.LLVMGetUndef(ty.ptr))

    @staticmethod
    def int(ty, value):
        check_is_type(ty)
        return _make_value(_core.LLVMConstInt(ty.ptr, value, 0))

    @staticmethod
    def int_signextend(ty, value):
        check_is_type(ty)
        return _make_value(_core.LLVMConstInt(ty.ptr, value, 1))

    @staticmethod
    def real(ty, value):
        check_is_type(ty)
        if isinstance(value, str):
            return _make_value(_core.LLVMConstRealOfString(ty.ptr, value))
        else:
            return _make_value(_core.LLVMConstReal(ty.ptr, value))

    @staticmethod
    def string(strval): # dont_null_terminate=True
        return _make_value(_core.LLVMConstString(strval, 1))

    @staticmethod
    def stringz(strval): # dont_null_terminate=False
        return _make_value(_core.LLVMConstString(strval, 0))

    @staticmethod
    def array(ty, consts):
        check_is_type(ty)
        const_ptrs = unpack_constants(consts)
        return _make_value(_core.LLVMConstArray(ty.ptr, const_ptrs))

    @staticmethod
    def struct(consts): # not packed
        const_ptrs = unpack_constants(consts)
        return _make_value(_core.LLVMConstStruct(const_ptrs, 0))

    @staticmethod
    def packed_struct(consts):
        const_ptrs = unpack_constants(consts)
        return _make_value(_core.LLVMConstStruct(const_ptrs, 1))

    @staticmethod
    def vector(consts):
        const_ptrs = unpack_constants(consts)
        return _make_value(_core.LLVMConstVector(const_ptrs))

    @staticmethod
    def sizeof(ty):
        check_is_type(ty)
        return _make_value(_core.LLVMSizeOf(ty.ptr))

    def neg(self):
        return _make_value(_core.LLVMConstNeg(self.ptr))

    def not_(self):
        return _make_value(_core.LLVMConstNot(self.ptr))

    def add(self, rhs):
        check_is_constant(rhs)
        return _make_value(_core.LLVMConstAdd(self.ptr, rhs.ptr))

    def fadd(self, rhs):
        check_is_constant(rhs)
        return _make_value(_core.LLVMConstFAdd(self.ptr, rhs.ptr))

    def sub(self, rhs):
        check_is_constant(rhs)
        return _make_value(_core.LLVMConstSub(self.ptr, rhs.ptr))

    def fsub(self, rhs):
        check_is_constant(rhs)
        return _make_value(_core.LLVMConstFSub(self.ptr, rhs.ptr))

    def mul(self, rhs):
        check_is_constant(rhs)
        return _make_value(_core.LLVMConstMul(self.ptr, rhs.ptr))

    def fmul(self, rhs):
        check_is_constant(rhs)
        return _make_value(_core.LLVMConstFMul(self.ptr, rhs.ptr))

    def udiv(self, rhs):
        check_is_constant(rhs)
        return _make_value(_core.LLVMConstUDiv(self.ptr, rhs.ptr))

    def sdiv(self, rhs):
        check_is_constant(rhs)
        return _make_value(_core.LLVMConstSDiv(self.ptr, rhs.ptr))

    def fdiv(self, rhs):
        check_is_constant(rhs)
        return _make_value(_core.LLVMConstFDiv(self.ptr, rhs.ptr))

    def urem(self, rhs):
        check_is_constant(rhs)
        return _make_value(_core.LLVMConstURem(self.ptr, rhs.ptr))

    def srem(self, rhs):
        check_is_constant(rhs)
        return _make_value(_core.LLVMConstSRem(self.ptr, rhs.ptr))

    def frem(self, rhs):
        check_is_constant(rhs)
        return _make_value(_core.LLVMConstFRem(self.ptr, rhs.ptr))

    def and_(self, rhs):
        check_is_constant(rhs)
        return _make_value(_core.LLVMConstAnd(self.ptr, rhs.ptr))

    def or_(self, rhs):
        check_is_constant(rhs)
        return _make_value(_core.LLVMConstOr(self.ptr, rhs.ptr))

    def xor(self, rhs):
        check_is_constant(rhs)
        return _make_value(_core.LLVMConstXor(self.ptr, rhs.ptr))

    def icmp(self, int_pred, rhs):
        check_is_constant(rhs)
        return _make_value(_core.LLVMConstICmp(int_pred, self.ptr, rhs.ptr))

    def fcmp(self, real_pred, rhs):
        check_is_constant(rhs)
        return _make_value(_core.LLVMConstFCmp(real_pred, self.ptr, rhs.ptr))

    def shl(self, rhs):
        check_is_constant(rhs)
        return _make_value(_core.LLVMConstShl(self.ptr, rhs.ptr))

    def lshr(self, rhs):
        check_is_constant(rhs)
        return _make_value(_core.LLVMConstLShr(self.ptr, rhs.ptr))

    def ashr(self, rhs):
        check_is_constant(rhs)
        return _make_value(_core.LLVMConstAShr(self.ptr, rhs.ptr))

    def gep(self, indices):
        index_ptrs = unpack_constants(indices)
        return _make_value(_core.LLVMConstGEP(self.ptr, index_ptrs))

    def trunc(self, ty):
        check_is_type(ty)
        return _make_value(_core.LLVMConstTrunc(self.ptr, ty.ptr))

    def sext(self, ty):
        check_is_type(ty)
        return _make_value(_core.LLVMConstSExt(self.ptr, ty.ptr))

    def zext(self, ty):
        check_is_type(ty)
        return _make_value(_core.LLVMConstZExt(self.ptr, ty.ptr))

    def fptrunc(self, ty):
        check_is_type(ty)
        return _make_value(_core.LLVMConstFPTrunc(self.ptr, ty.ptr))

    def fpext(self, ty):
        check_is_type(ty)
        return _make_value(_core.LLVMConstFPExt(self.ptr, ty.ptr))

    def uitofp(self, ty):
        check_is_type(ty)
        return _make_value(_core.LLVMConstUIToFP(self.ptr, ty.ptr))

    def sitofp(self, ty):
        check_is_type(ty)
        return _make_value(_core.LLVMConstSIToFP(self.ptr, ty.ptr))

    def fptoui(self, ty):
        check_is_type(ty)
        return _make_value(_core.LLVMConstFPToUI(self.ptr, ty.ptr))

    def fptosi(self, ty):
        check_is_type(ty)
        return _make_value(_core.LLVMConstFPToSI(self.ptr, ty.ptr))

    def ptrtoint(self, ty):
        check_is_type(ty)
        return _make_value(_core.LLVMConstPtrToInt(self.ptr, ty.ptr))

    def inttoptr(self, ty):
        check_is_type(ty)
        return _make_value(_core.LLVMConstIntToPtr(self.ptr, ty.ptr))

    def bitcast(self, ty):
        check_is_type(ty)
        return _make_value(_core.LLVMConstBitCast(self.ptr, ty.ptr))

    def select(self, true_const, false_const):
        check_is_constant(true_const)
        check_is_constant(false_const)
        return _make_value(
            _core.LLVMConstSelect(self.ptr, true_const.ptr, false_const.ptr))

    def extract_element(self, index): # note: self must be a _vector_ constant
        check_is_constant(index)
        return _make_value(
            _core.LLVMConstExtractElement(self.ptr, index.ptr))

    def insert_element(self, value, index):
        # note: self must be a _vector_ constant
        check_is_constant(value)
        check_is_constant(index)
        return _make_value(
            _core.LLVMConstInsertElement(self.ptr, value.ptr, index.ptr))

    def shuffle_vector(self, vector_b, mask):
        # note: self must be a _vector_ constant
        check_is_constant(vector_b)
        # note: vector_b must be a _vector_ constant
        check_is_constant(mask)
        return _make_value(
            _core.LLVMConstShuffleVector(self.ptr, vector_b.ptr, mask.ptr))


class ConstantExpr(Constant):
    pass


class ConstantAggregateZero(Constant):
    pass


class ConstantInt(Constant):
    pass


class ConstantFP(Constant):
    pass


class ConstantArray(Constant):
    pass


class ConstantStruct(Constant):
    pass


class ConstantVector(Constant):
    pass


class ConstantPointerNull(Constant):
    pass


class UndefValue(Constant):
    pass


class GlobalValue(Constant):

    def __init__(self, ptr):
        Constant.__init__(self, ptr)
        # Hang on to the module, don't let it die before we do.
        # It is nice to have just a map of functions without
        # retaining a ref to the owning module.
        self._module_obj = self.module

    def _delete(self):
        # Called in subclass delete() methods.
        self._module_obj = None

    def _get_linkage(self):
        return _core.LLVMGetLinkage(self.ptr)
    def _set_linkage(self, value):
        _core.LLVMSetLinkage(self.ptr, value)
    linkage = property(_get_linkage, _set_linkage)

    def _get_section(self):
        return _core.LLVMGetSection(self.ptr)
    def _set_section(self, value):
        return _core.LLVMSetSection(self.ptr, value)
    section = property(_get_section, _set_section)

    def _get_visibility(self):
        return _core.LLVMGetVisibility(self.ptr)
    def _set_visibility(self, value):
        return _core.LLVMSetVisibility(self.ptr, value)
    visibility = property(_get_visibility, _set_visibility)

    def _get_alignment(self):
        return _core.LLVMGetAlignment(self.ptr)
    def _set_alignment(self, value):
        return _core.LLVMSetAlignment(self.ptr, value)
    alignment = property(_get_alignment, _set_alignment)

    @property
    def is_declaration(self):
        return _core.LLVMIsDeclaration(self.ptr) != 0

    @property
    def module(self):
        return Module(_core.LLVMGetGlobalParent(self.ptr))


class GlobalVariable(GlobalValue):

    @staticmethod
    def new(module, ty, name):
        check_is_module(module)
        check_is_type(ty)
        return _make_value(_core.LLVMAddGlobal(module.ptr, ty.ptr, name))

    @staticmethod
    def get(module, name):
        check_is_module(module)
        ptr = _core.LLVMGetNamedGlobal(module.ptr, name)
        if not ptr:
            raise llvm.LLVMException, ("no global named `%s`" % name)
        return _make_value(ptr)

    def delete(self):
        self._delete()
        _core.LLVMDeleteGlobal(self.ptr)
        self.forget()
        self.ptr = None

    def _get_initializer(self):
        if _core.LLVMHasInitializer(self.ptr):
            return _make_value(_core.LLVMGetInitializer(self.ptr))
        else:
            return None

    def _set_initializer(self, const):
        check_is_constant(const)
        _core.LLVMSetInitializer(self.ptr, const.ptr)

    initializer = property(_get_initializer, _set_initializer)

    def _get_is_global_constant(self):
        return _core.LLVMIsGlobalConstant(self.ptr)

    def _set_is_global_constant(self, value):
        value = _to_int(value)
        _core.LLVMSetGlobalConstant(self.ptr, value)

    global_constant = \
        property(_get_is_global_constant, _set_is_global_constant)


class Argument(Value):

    def add_attribute(self, attr):
        _core.LLVMAddAttribute(self.ptr, attr)

    def remove_attribute(self, attr):
        _core.LLVMRemoveAttribute(self.ptr, attr)

    def _set_alignment(self, align):
        _core.LLVMSetParamAlignment(self.ptr, align)

    def _get_alignment(self):
        return _core.LLVMGetParamAlignment(self.ptr)

    alignment = \
        property(_get_alignment, _set_alignment)


class Function(GlobalValue):

    @staticmethod
    def new(module, func_ty, name):
        check_is_module(module)
        check_is_type(func_ty)
        return _make_value(_core.LLVMAddFunction(module.ptr, name,
            func_ty.ptr))

    @staticmethod
    def get_or_insert(module, func_ty, name):
        check_is_module(module)
        check_is_type(func_ty)
        return _make_value(_core.LLVMModuleGetOrInsertFunction(module.ptr,
            name, func_ty.ptr))

    @staticmethod
    def get(module, name):
        check_is_module(module)
        ptr = _core.LLVMGetNamedFunction(module.ptr, name)
        if not ptr:
            raise llvm.LLVMException, ("no function named `%s`" % name)
        return _make_value(ptr)

    @staticmethod
    def intrinsic(module, intrinsic_id, types):
        check_is_module(module)
        ptrs = unpack_types(types)
        return _make_value(
            _core.LLVMGetIntrinsic(module.ptr, intrinsic_id, ptrs))

    def delete(self):
        self._delete()
        _core.LLVMDeleteFunction(self.ptr)
        self.forget()
        self.ptr = None

    @property
    def intrinsic_id(self):
        return _core.LLVMGetIntrinsicID(self.ptr)

    def _get_cc(self): return _core.LLVMGetFunctionCallConv(self.ptr)
    def _set_cc(self, value): _core.LLVMSetFunctionCallConv(self.ptr, value)
    calling_convention = property(_get_cc, _set_cc)

    def _get_coll(self): return _core.LLVMGetGC(self.ptr)
    def _set_coll(self, value): _core.LLVMSetGC(self.ptr, value)
    collector = property(_get_coll, _set_coll)

    # the nounwind attribute:
    def _get_does_not_throw(self): return _core.LLVMGetDoesNotThrow(self.ptr)
    def _set_does_not_throw(self,value):  _core.LLVMSetDoesNotThrow(self.ptr, value)
    does_not_throw = property(_get_does_not_throw, _set_does_not_throw)

    @property
    def args(self):
        return _util.wrapiter(_core.LLVMGetFirstParam,
            _core.LLVMGetNextParam, self.ptr, _make_value)

    @property
    def basic_block_count(self):
        return _core.LLVMCountBasicBlocks(self.ptr)

    @property
    def entry_basic_block(self):
        if self.basic_block_count == 0:
            return None
        return _make_value(_core.LLVMGetEntryBasicBlock(self.ptr))

    def get_entry_basic_block(self):
        """Deprecated, use entry_basic_block property."""
        return self.entry_basic_block

    def append_basic_block(self, name):
        return _make_value(_core.LLVMAppendBasicBlock(self.ptr, name))

    @property
    def basic_blocks(self):
        return _util.wrapiter(_core.LLVMGetFirstBasicBlock,
            _core.LLVMGetNextBasicBlock, self.ptr, _make_value)

    def viewCFG(self):
        return _core.LLVMViewFunctionCFG(self.ptr)

    def add_attribute(self, attr):
        _core.LLVMAddFunctionAttr(self.ptr, attr)

    def remove_attribute(self, attr):
        _core.LLVMRemoveFunctionAttr(self.ptr, attr)

    def viewCFGOnly(self):
        return _core.LLVMViewFunctionCFGOnly(self.ptr)

    def verify(self):
        # Although we're just asking LLVM to return the success or
        # failure, it appears to print result to stderr and abort.
        return _core.LLVMVerifyFunction(self.ptr) != 0

#===----------------------------------------------------------------------===
# Instruction
#===----------------------------------------------------------------------===

class Instruction(User):

    @property
    def basic_block(self):
        return _make_value(_core.LLVMGetInstructionParent(self.ptr))

    @property
    def is_terminator(self):
        return _core.LLVMInstIsTerminator(self.ptr) != 0

    @property
    def is_binary_op(self):
        return _core.LLVMInstIsBinaryOp(self.ptr) != 0

    @property
    def is_shift(self):
        return _core.LLVMInstIsShift(self.ptr) != 0

    @property
    def is_cast(self):
        return _core.LLVMInstIsCast(self.ptr) != 0

    @property
    def is_logical_shift(self):
        return _core.LLVMInstIsLogicalShift(self.ptr) != 0

    @property
    def is_arithmetic_shift(self):
        return _core.LLVMInstIsArithmeticShift(self.ptr) != 0

    @property
    def is_associative(self):
        return _core.LLVMInstIsAssociative(self.ptr) != 0

    @property
    def is_commutative(self):
        return _core.LLVMInstIsCommutative(self.ptr) != 0

    @property
    def is_volatile(self):
        """True if this is a volatile load or store."""
        return _core.LLVMInstIsVolatile(self.ptr) != 0

    @property
    def opcode(self):
        return _core.LLVMInstGetOpcode(self.ptr)

    @property
    def opcode_name(self):
        return _core.LLVMInstGetOpcodeName(self.ptr)


class CallOrInvokeInstruction(Instruction):

    def _get_cc(self): return _core.LLVMGetInstructionCallConv(self.ptr)
    def _set_cc(self, value): _core.LLVMSetInstructionCallConv(self.ptr, value)
    calling_convention = property(_get_cc, _set_cc)

    def add_parameter_attribute(self, idx, attr):
        _core.LLVMAddInstrAttribute(self.ptr, idx, attr)

    def remove_parameter_attribute(self, idx, attr):
        _core.LLVMRemoveInstrAttribute(self.ptr, idx, attr)

    def set_parameter_alignment(self, idx, align):
        _core.LLVMSetInstrParamAlignment(self.ptr, idx, align)

    # tail call is valid only for 'call', not 'invoke'
    # disabled for now
    #def _get_tc(self): return _core.LLVMIsTailCall(self.ptr)
    #def _set_tc(self, value): _core.LLVMSetTailCall(self.ptr, value)
    #tail_call = property(_get_tc, _set_tc)


class PHINode(Instruction):

    @property
    def incoming_count(self):
        return _core.LLVMCountIncoming(self.ptr)

    def add_incoming(self, value, block):
        check_is_value(value)
        check_is_basic_block(block)
        _core.LLVMAddIncoming1(self.ptr, value.ptr, block.ptr)

    def get_incoming_value(self, idx):
        return _make_value(_core.LLVMGetIncomingValue(self.ptr, idx))

    def get_incoming_block(self, idx):
        return _make_value(_core.LLVMGetIncomingBlock(self.ptr, idx))


class SwitchInstruction(Instruction):

    def add_case(self, const, bblk):
        check_is_constant(const) # and has to be an int too
        check_is_basic_block(bblk)
        _core.LLVMAddCase(self.ptr, const.ptr, bblk.ptr)


class CompareInstruction(Instruction):

    @property
    def predicate(self):
        return _core.LLVMCmpInstGetPredicate(self.ptr)


#===----------------------------------------------------------------------===
# Basic block
#===----------------------------------------------------------------------===

class BasicBlock(Value):

    def insert_before(self, name):
        return _make_value(_core.LLVMInsertBasicBlock(self.ptr, name))

    def delete(self):
        _core.LLVMDeleteBasicBlock(self.ptr)
        self.forget()
        self.ptr = None

    @property
    def function(self):
        func_ptr = _core.LLVMGetBasicBlockParent(self.ptr)
        return _make_value(func_ptr)

    @property
    def instructions(self):
        return _util.wrapiter(_core.LLVMGetFirstInstruction,
            _core.LLVMGetNextInstruction, self.ptr, _make_value)


#===----------------------------------------------------------------------===
# Value factory method
#===----------------------------------------------------------------------===

# value ID -> class map
__class_for_valueid = {
    VALUE_ARGUMENT                        : Argument,
    VALUE_BASIC_BLOCK                     : BasicBlock,
    VALUE_FUNCTION                        : Function,
    VALUE_GLOBAL_ALIAS                    : GlobalValue,
    VALUE_GLOBAL_VARIABLE                 : GlobalVariable,
    VALUE_UNDEF_VALUE                     : UndefValue,
    VALUE_CONSTANT_EXPR                   : ConstantExpr,
    VALUE_CONSTANT_AGGREGATE_ZERO         : ConstantAggregateZero,
    VALUE_CONSTANT_INT                    : ConstantInt,
    VALUE_CONSTANT_FP                     : ConstantFP,
    VALUE_CONSTANT_ARRAY                  : ConstantArray,
    VALUE_CONSTANT_STRUCT                 : ConstantStruct,
    VALUE_CONSTANT_VECTOR                 : ConstantVector,
    VALUE_CONSTANT_POINTER_NULL           : ConstantPointerNull,
    VALUE_INSTRUCTION + OPCODE_PHI        : PHINode,
    VALUE_INSTRUCTION + OPCODE_CALL       : CallOrInvokeInstruction,
    VALUE_INSTRUCTION + OPCODE_INVOKE     : CallOrInvokeInstruction,
    VALUE_INSTRUCTION + OPCODE_SWITCH     : SwitchInstruction,
    VALUE_INSTRUCTION + OPCODE_ICMP       : CompareInstruction,
    VALUE_INSTRUCTION + OPCODE_FCMP       : CompareInstruction
}

def _make_value(ptr):
    kind = _core.LLVMValueGetID(ptr)
    # based on kind, create one of the Value subclasses
    class_obj = __class_for_valueid.get(kind)
    if class_obj:
        return class_obj(ptr)
    elif kind > VALUE_INSTRUCTION:
        # "generic" instruction
        return Instruction(ptr)
    else:
        # "generic" value
        return Value(ptr)


#===----------------------------------------------------------------------===
# Builder
#===----------------------------------------------------------------------===

class Builder(object):

    @staticmethod
    def new(basic_block):
        check_is_basic_block(basic_block)
        b = Builder(_core.LLVMCreateBuilder())
        b.position_at_end(basic_block)
        return b

    def __init__(self, ptr):
        self.ptr = ptr

    def __del__(self):
        _core.LLVMDisposeBuilder(self.ptr)

    def position_at_beginning(self, bblk):
        """Position the builder at the beginning of the given block.

        Next instruction inserted will be first one in the block."""
        check_is_basic_block(bblk)
        # Avoids using "blk.instructions", which will fetch all the
        # instructions into a list. Don't try this at home, though.
        inst_ptr = _core.LLVMGetFirstInstruction(bblk.ptr)
        if inst_ptr:
            # Issue #10: inst_ptr can be None if b/b has no insts.
            inst = _make_value(inst_ptr)
            self.position_before(inst)

    def position_at_end(self, bblk):
        """Position the builder at the end of the given block.

        Next instruction inserted will be last one in the block."""
        _core.LLVMPositionBuilderAtEnd(self.ptr, bblk.ptr)

    def position_before(self, instr):
        """Position the builder before the given instruction.

        The instruction can belong to a basic block other than the
        current one."""
        _core.LLVMPositionBuilderBefore(self.ptr, instr.ptr)

    @property
    def block(self):
        """Deprecated, use basic_block property instead."""
        return _make_value(_core.LLVMGetInsertBlock(self.ptr))

    @property
    def basic_block(self):
        """The basic block where the builder is positioned."""
        return _make_value(_core.LLVMGetInsertBlock(self.ptr))

    # terminator instructions

    def ret_void(self):
        return _make_value(_core.LLVMBuildRetVoid(self.ptr))

    def ret(self, value):
        check_is_value(value)
        return _make_value(_core.LLVMBuildRet(self.ptr, value.ptr))

    def ret_many(self, values):
        vs = unpack_values(values)
        return _make_value(_core.LLVMBuildRetMultiple(self.ptr, vs))

    def branch(self, bblk):
        check_is_basic_block(bblk)
        return _make_value(_core.LLVMBuildBr(self.ptr, bblk.ptr))

    def cbranch(self, if_value, then_blk, else_blk):
        check_is_value(if_value)
        check_is_basic_block(then_blk)
        check_is_basic_block(else_blk)
        return _make_value(
            _core.LLVMBuildCondBr(self.ptr,
                if_value.ptr, then_blk.ptr, else_blk.ptr))

    def switch(self, value, else_blk, n=10):
        check_is_value(value)  # value has to be of any 'int' type
        check_is_basic_block(else_blk)
        return _make_value(
            _core.LLVMBuildSwitch(self.ptr, value.ptr, else_blk.ptr, n))

    def invoke(self, func, args, then_blk, catch_blk, name=""):
        check_is_callable(func)
        check_is_basic_block(then_blk)
        check_is_basic_block(catch_blk)
        args2 = unpack_values(args)
        return _make_value(
            _core.LLVMBuildInvoke(self.ptr, func.ptr, args2,
                then_blk.ptr, catch_blk.ptr, name))

    def unwind(self):
        return _make_value(_core.LLVMBuildUnwind(self.ptr))

    def unreachable(self):
        return _make_value(_core.LLVMBuildUnreachable(self.ptr))

    # arithmethic, bitwise and logical

    def add(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return _make_value(_core.LLVMBuildAdd(self.ptr, lhs.ptr, rhs.ptr, name))

    def fadd(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return _make_value(_core.LLVMBuildFAdd(self.ptr, lhs.ptr, rhs.ptr, name))

    def sub(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return _make_value(_core.LLVMBuildSub(self.ptr, lhs.ptr, rhs.ptr, name))

    def fsub(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return _make_value(_core.LLVMBuildFSub(self.ptr, lhs.ptr, rhs.ptr, name))

    def mul(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return _make_value(_core.LLVMBuildMul(self.ptr, lhs.ptr, rhs.ptr, name))

    def fmul(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return _make_value(_core.LLVMBuildFMul(self.ptr, lhs.ptr, rhs.ptr, name))

    def udiv(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return _make_value(
            _core.LLVMBuildUDiv(self.ptr, lhs.ptr, rhs.ptr, name))

    def sdiv(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return _make_value(
            _core.LLVMBuildSDiv(self.ptr, lhs.ptr, rhs.ptr, name))

    def fdiv(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return _make_value(
            _core.LLVMBuildFDiv(self.ptr, lhs.ptr, rhs.ptr, name))

    def urem(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return _make_value(
            _core.LLVMBuildURem(self.ptr, lhs.ptr, rhs.ptr, name))

    def srem(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return _make_value(
            _core.LLVMBuildSRem(self.ptr, lhs.ptr, rhs.ptr, name))

    def frem(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return _make_value(
            _core.LLVMBuildFRem(self.ptr, lhs.ptr, rhs.ptr, name))

    def shl(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return _make_value(
            _core.LLVMBuildShl(self.ptr, lhs.ptr, rhs.ptr, name))

    def lshr(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return _make_value(
            _core.LLVMBuildLShr(self.ptr, lhs.ptr, rhs.ptr, name))

    def ashr(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return _make_value(
            _core.LLVMBuildAShr(self.ptr, lhs.ptr, rhs.ptr, name))

    def and_(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return _make_value(
            _core.LLVMBuildAnd(self.ptr, lhs.ptr, rhs.ptr, name))

    def or_(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return _make_value(
            _core.LLVMBuildOr(self.ptr, lhs.ptr, rhs.ptr, name))

    def xor(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return _make_value(
            _core.LLVMBuildXor(self.ptr, lhs.ptr, rhs.ptr, name))

    def neg(self, val, name=""):
        check_is_value(val)
        return _make_value(_core.LLVMBuildNeg(self.ptr, val.ptr, name))

    def not_(self, val, name=""):
        check_is_value(val)
        return _make_value(_core.LLVMBuildNot(self.ptr, val.ptr, name))

    # memory

    def malloc(self, ty, name=""):
        check_is_type(ty)
        return _make_value(_core.LLVMBuildMalloc(self.ptr, ty.ptr, name))

    def malloc_array(self, ty, size, name=""):
        check_is_type(ty)
        check_is_value(size)
        return _make_value(
            _core.LLVMBuildArrayMalloc(self.ptr, ty.ptr, size.ptr, name))

    def alloca(self, ty, name=""):
        check_is_type(ty)
        return _make_value(_core.LLVMBuildAlloca(self.ptr, ty.ptr, name))

    def alloca_array(self, ty, size, name=""):
        check_is_type(ty)
        check_is_value(size)
        return _make_value(
            _core.LLVMBuildArrayAlloca(self.ptr, ty.ptr, size.ptr, name))

    def free(self, ptr):
        check_is_value(ptr)
        return _make_value(_core.LLVMBuildFree(self.ptr, ptr.ptr))

    def load(self, ptr, name=""):
        check_is_value(ptr)
        return _make_value(_core.LLVMBuildLoad(self.ptr, ptr.ptr, name))

    def store(self, value, ptr):
        check_is_value(value)
        check_is_value(ptr)
        return _make_value(_core.LLVMBuildStore(self.ptr, value.ptr, ptr.ptr))

    def gep(self, ptr, indices, name=""):
        check_is_value(ptr)
        index_ptrs = unpack_values(indices)
        return _make_value(
            _core.LLVMBuildGEP(self.ptr, ptr.ptr, index_ptrs, name))

    # casts and extensions

    def trunc(self, value, dest_ty, name=""):
        check_is_value(value)
        check_is_type(dest_ty)
        return _make_value(
            _core.LLVMBuildTrunc(self.ptr, value.ptr, dest_ty.ptr, name))

    def zext(self, value, dest_ty, name=""):
        check_is_value(value)
        check_is_type(dest_ty)
        return _make_value(
            _core.LLVMBuildZExt(self.ptr, value.ptr, dest_ty.ptr, name))

    def sext(self, value, dest_ty, name=""):
        check_is_value(value)
        check_is_type(dest_ty)
        return _make_value(
            _core.LLVMBuildSExt(self.ptr, value.ptr, dest_ty.ptr, name))

    def fptoui(self, value, dest_ty, name=""):
        check_is_value(value)
        check_is_type(dest_ty)
        return _make_value(
            _core.LLVMBuildFPToUI(self.ptr, value.ptr, dest_ty.ptr, name))

    def fptosi(self, value, dest_ty, name=""):
        check_is_value(value)
        check_is_type(dest_ty)
        return _make_value(
            _core.LLVMBuildFPToSI(self.ptr, value.ptr, dest_ty.ptr, name))

    def uitofp(self, value, dest_ty, name=""):
        check_is_value(value)
        check_is_type(dest_ty)
        return _make_value(
            _core.LLVMBuildUIToFP(self.ptr, value.ptr, dest_ty.ptr, name))

    def sitofp(self, value, dest_ty, name=""):
        check_is_value(value)
        check_is_type(dest_ty)
        return _make_value(
            _core.LLVMBuildSIToFP(self.ptr, value.ptr, dest_ty.ptr, name))

    def fptrunc(self, value, dest_ty, name=""):
        check_is_value(value)
        check_is_type(dest_ty)
        return _make_value(
            _core.LLVMBuildFPTrunc(self.ptr, value.ptr, dest_ty.ptr, name))

    def fpext(self, value, dest_ty, name=""):
        check_is_value(value)
        check_is_type(dest_ty)
        return _make_value(
            _core.LLVMBuildFPExt(self.ptr, value.ptr, dest_ty.ptr, name))

    def ptrtoint(self, value, dest_ty, name=""):
        check_is_value(value)
        check_is_type(dest_ty)
        return _make_value(
            _core.LLVMBuildPtrToInt(self.ptr, value.ptr, dest_ty.ptr, name))

    def inttoptr(self, value, dest_ty, name=""):
        check_is_value(value)
        check_is_type(dest_ty)
        return _make_value(
            _core.LLVMBuildIntToPtr(self.ptr, value.ptr, dest_ty.ptr, name))

    def bitcast(self, value, dest_ty, name=""):
        check_is_value(value)
        check_is_type(dest_ty)
        return _make_value(
            _core.LLVMBuildBitCast(self.ptr, value.ptr, dest_ty.ptr, name))

    # comparisons

    def icmp(self, ipred, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return _make_value(
            _core.LLVMBuildICmp(self.ptr, ipred, lhs.ptr, rhs.ptr, name))

    def fcmp(self, rpred, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return _make_value(
            _core.LLVMBuildFCmp(self.ptr, rpred, lhs.ptr, rhs.ptr, name))

    # misc

    def extract_value(self, retval, idx, name=""):
        check_is_value(retval)
        return _make_value(
            _core.LLVMBuildGetResult(self.ptr, retval.ptr, idx, name))

    # obsolete synonym for extract_value
    getresult = extract_value

    def phi(self, ty, name=""):
        check_is_type(ty)
        return _make_value(_core.LLVMBuildPhi(self.ptr, ty.ptr, name))

    def call(self, fn, args, name=""):
        check_is_callable(fn)
        arg_ptrs = unpack_values(args)
        return _make_value(
            _core.LLVMBuildCall(self.ptr, fn.ptr, arg_ptrs, name))

    def select(self, cond, then_value, else_value, name=""):
        check_is_value(cond)
        check_is_value(then_value)
        check_is_value(else_value)
        return _make_value(
            _core.LLVMBuildSelect(self.ptr, cond.ptr,
                then_value.ptr, else_value.ptr, name))

    def vaarg(self, list_val, ty, name=""):
        check_is_value(list_val)
        check_is_type(ty)
        return _make_value(
            _core.LLVMBuildVAArg(self.ptr, list_val.ptr, ty.ptr, name))

    def extract_element(self, vec_val, idx_val, name=""):
        check_is_value(vec_val)
        check_is_value(idx_val)
        return _make_value(
            _core.LLVMBuildExtractElement(self.ptr, vec_val.ptr,
                idx_val.ptr, name))

    def insert_element(self, vec_val, elt_val, idx_val, name=""):
        check_is_value(vec_val)
        check_is_value(elt_val)
        check_is_value(idx_val)
        return _make_value(
            _core.LLVMBuildInsertElement(self.ptr, vec_val.ptr,
                elt_val.ptr, idx_val.ptr, name))

    def shuffle_vector(self, vecA, vecB, mask, name=""):
        check_is_value(vecA)
        check_is_value(vecB)
        check_is_value(mask)
        return _make_value(
            _core.LLVMBuildShuffleVector(self.ptr,
                vecA.ptr, vecB.ptr, mask.ptr, name))


#===----------------------------------------------------------------------===
# Memory buffer
#===----------------------------------------------------------------------===

class MemoryBuffer(object):

    @staticmethod
    def from_file(fname):
        ret = _core.LLVMCreateMemoryBufferWithContentsOfFile(fname)
        if isinstance(ret, str):
            return (None, ret)
        else:
            obj = MemoryBuffer(ret)
            return (obj, "")

    @staticmethod
    def from_stdin():
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
# Misc
#===----------------------------------------------------------------------===

def load_library_permanently(filename):
    """Load a shared library.

    Load the given shared library (filename argument specifies the full
    path of the .so file) using LLVM. Symbols from these are available
    from the execution engine thereafter."""

    ret = _core.LLVMLoadLibraryPermanently(filename)
    if isinstance(ret, str):
        raise llvm.LLVMException, ret

def inline_function(call):
    check_is_value(call)
    return _core.LLVMInlineFunction(call.ptr)

