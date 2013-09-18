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

from io import BytesIO
try:
    from StringIO import StringIO
except ImportError:
    try:
        from cStringIO import StringIO
    except ImportError:
        from io import StringIO

import contextlib, weakref

import llvm
from llvm._intrinsic_ids import *

from llvmpy import api

#===----------------------------------------------------------------------===
# Enumerations
#===----------------------------------------------------------------------===
class Enum(int):
    '''Overload integer to print the name of the enum.
    '''
    def __repr__(self):
        return '%s(%d)' % (type(self).__name__, self)

    @classmethod
    def declare(cls):
        declared = cls._declared_ = {}
        scope = globals()
        for name in filter(lambda s: s.startswith(cls.prefix), dir(cls)):
            n = getattr(cls, name)
            typ = type(name, (cls,), {})
            obj = typ(n)
            declared[n] = obj
            scope[name] = obj

    @classmethod
    def get(cls, num):
        return cls._declared_[num]

# type id (llvm::Type::TypeID)
class TypeEnum(Enum):
    prefix = 'TYPE_'
    TypeID = api.llvm.Type.TypeID

    TYPE_VOID       = TypeID.VoidTyID
    TYPE_HALF       = TypeID.HalfTyID
    TYPE_FLOAT      = TypeID.FloatTyID
    TYPE_DOUBLE     = TypeID.DoubleTyID
    TYPE_X86_FP80   = TypeID.X86_FP80TyID
    TYPE_FP128      = TypeID.FP128TyID
    TYPE_PPC_FP128  = TypeID.PPC_FP128TyID
    TYPE_LABEL      = TypeID.LabelTyID
    TYPE_INTEGER    = TypeID.IntegerTyID
    TYPE_FUNCTION   = TypeID.FunctionTyID
    TYPE_STRUCT     = TypeID.StructTyID
    TYPE_ARRAY      = TypeID.ArrayTyID
    TYPE_POINTER    = TypeID.PointerTyID
    TYPE_VECTOR     = TypeID.VectorTyID
    TYPE_METADATA   = TypeID.MetadataTyID
    TYPE_X86_MMX    = TypeID.X86_MMXTyID

TypeEnum.declare()


# value IDs (llvm::Value::ValueTy enum)
# According to the doxygen docs, it is not a good idea to use these enums.
# There are more values than those declared.
class ValueEnum(Enum):
    prefix = 'VALUE_'
    ValueTy = api.llvm.Value.ValueTy

    VALUE_ARGUMENT                          = ValueTy.ArgumentVal
    VALUE_BASIC_BLOCK                       = ValueTy.BasicBlockVal
    VALUE_FUNCTION                          = ValueTy.FunctionVal
    VALUE_GLOBAL_ALIAS                      = ValueTy.GlobalAliasVal
    VALUE_GLOBAL_VARIABLE                   = ValueTy.GlobalVariableVal
    VALUE_UNDEF_VALUE                       = ValueTy.UndefValueVal
    VALUE_BLOCK_ADDRESS                     = ValueTy.BlockAddressVal
    VALUE_CONSTANT_EXPR                     = ValueTy.ConstantExprVal
    VALUE_CONSTANT_AGGREGATE_ZERO           = ValueTy.ConstantAggregateZeroVal
    VALUE_CONSTANT_DATA_ARRAY               = ValueTy.ConstantDataArrayVal
    VALUE_CONSTANT_DATA_VECTOR              = ValueTy.ConstantDataVectorVal
    VALUE_CONSTANT_INT                      = ValueTy.ConstantIntVal
    VALUE_CONSTANT_FP                       = ValueTy.ConstantFPVal
    VALUE_CONSTANT_ARRAY                    = ValueTy.ConstantArrayVal
    VALUE_CONSTANT_STRUCT                   = ValueTy.ConstantStructVal
    VALUE_CONSTANT_VECTOR                   = ValueTy.ConstantVectorVal
    VALUE_CONSTANT_POINTER_NULL             = ValueTy.ConstantPointerNullVal
    VALUE_MD_NODE                           = ValueTy.MDNodeVal
    VALUE_MD_STRING                         = ValueTy.MDStringVal
    VALUE_INLINE_ASM                        = ValueTy.InlineAsmVal
    VALUE_PSEUDO_SOURCE_VALUE               = ValueTy.PseudoSourceValueVal
    VALUE_FIXED_STACK_PSEUDO_SOURCE_VALUE   = ValueTy.FixedStackPseudoSourceValueVal
    VALUE_INSTRUCTION                       = ValueTy.InstructionVal

ValueEnum.declare()

# instruction opcodes (from include/llvm/Instruction.def)
class OpcodeEnum(Enum):
    prefix = 'OPCODE_'

    OPCODE_RET            = 1
    OPCODE_BR             = 2
    OPCODE_SWITCH         = 3
    OPCODE_INDIRECT_BR    = 4
    OPCODE_INVOKE         = 5
    OPCODE_RESUME         = 6
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
    OPCODE_FENCE          = 30
    OPCODE_ATOMICCMPXCHG  = 31
    OPCODE_ATOMICRMW      = 32
    OPCODE_TRUNC          = 33
    OPCODE_ZEXT           = 34
    OPCODE_SEXT           = 35
    OPCODE_FPTOUI         = 36
    OPCODE_FPTOSI         = 37
    OPCODE_UITOFP         = 38
    OPCODE_SITOFP         = 39
    OPCODE_FPTRUNC        = 40
    OPCODE_FPEXT          = 41
    OPCODE_PTRTOINT       = 42
    OPCODE_INTTOPTR       = 43
    OPCODE_BITCAST        = 44
    OPCODE_ICMP           = 45
    OPCODE_FCMP           = 46
    OPCODE_PHI            = 47
    OPCODE_CALL           = 48
    OPCODE_SELECT         = 49
    OPCODE_USEROP1        = 50
    OPCODE_USEROP2        = 51
    OPCODE_VAARG          = 52
    OPCODE_EXTRACTELEMENT = 53
    OPCODE_INSERTELEMENT  = 54
    OPCODE_SHUFFLEVECTOR  = 55
    OPCODE_EXTRACTVALUE   = 56
    OPCODE_INSERTVALUE    = 57
    OPCODE_LANDINGPAD     = 58

OpcodeEnum.declare()

# calling conventions

class CCEnum(Enum):
    prefix = 'CC_'

    ID = api.llvm.CallingConv.ID

    CC_C             = ID.C
    CC_FASTCALL      = ID.Fast
    CC_COLDCALL      = ID.Cold
    CC_GHC           = ID.GHC
    CC_X86_STDCALL   = ID.X86_StdCall
    CC_X86_FASTCALL  = ID.X86_FastCall
    CC_ARM_APCS      = ID.ARM_APCS
    CC_ARM_AAPCS     = ID.ARM_AAPCS
    CC_ARM_AAPCS_VFP = ID.ARM_AAPCS_VFP
    CC_MSP430_INTR   = ID.MSP430_INTR
    CC_X86_THISCALL  = ID.X86_ThisCall
    CC_PTX_KERNEL    = ID.PTX_Kernel
    CC_PTX_DEVICE    = ID.PTX_Device

    if llvm.version <= (3, 3):
        CC_MBLAZE_INTR   = ID.MBLAZE_INTR
        CC_MBLAZE_SVOL   = ID.MBLAZE_SVOL

CCEnum.declare()

# int predicates
class ICMPEnum(Enum):
    prefix = 'ICMP_'

    Predicate = api.llvm.CmpInst.Predicate

    ICMP_EQ         = Predicate.ICMP_EQ
    ICMP_NE         = Predicate.ICMP_NE
    ICMP_UGT        = Predicate.ICMP_UGT
    ICMP_UGE        = Predicate.ICMP_UGE
    ICMP_ULT        = Predicate.ICMP_ULT
    ICMP_ULE        = Predicate.ICMP_ULE
    ICMP_SGT        = Predicate.ICMP_SGT
    ICMP_SGE        = Predicate.ICMP_SGE
    ICMP_SLT        = Predicate.ICMP_SLT
    ICMP_SLE        = Predicate.ICMP_SLE

ICMPEnum.declare()
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

class FCMPEnum(Enum):
    prefix = 'FCMP_'

    Predicate = api.llvm.CmpInst.Predicate

    FCMP_FALSE      = Predicate.FCMP_FALSE
    FCMP_OEQ        = Predicate.FCMP_OEQ
    FCMP_OGT        = Predicate.FCMP_OGT
    FCMP_OGE        = Predicate.FCMP_OGE
    FCMP_OLT        = Predicate.FCMP_OLT
    FCMP_OLE        = Predicate.FCMP_OLE
    FCMP_ONE        = Predicate.FCMP_ONE
    FCMP_ORD        = Predicate.FCMP_ORD
    FCMP_UNO        = Predicate.FCMP_UNO
    FCMP_UEQ        = Predicate.FCMP_UEQ
    FCMP_UGT        = Predicate.FCMP_UGT
    FCMP_UGE        = Predicate.FCMP_UGE
    FCMP_ULT        = Predicate.FCMP_ULT
    FCMP_ULE        = Predicate.FCMP_ULE
    FCMP_UNE        = Predicate.FCMP_UNE
    FCMP_TRUE       = Predicate.FCMP_TRUE

FCMPEnum.declare()

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

# linkages (see llvm::GlobalValue::LinkageTypes)
class LinkageEnum(Enum):
    prefix = 'LINKAGE_'
    LinkageTypes = api.llvm.GlobalValue.LinkageTypes

    LINKAGE_EXTERNAL                =  LinkageTypes.ExternalLinkage
    LINKAGE_AVAILABLE_EXTERNALLY    =  LinkageTypes.AvailableExternallyLinkage
    LINKAGE_LINKONCE_ANY            =  LinkageTypes.LinkOnceAnyLinkage
    LINKAGE_LINKONCE_ODR            =  LinkageTypes.LinkOnceODRLinkage
    LINKAGE_WEAK_ANY                =  LinkageTypes.WeakAnyLinkage
    LINKAGE_WEAK_ODR                =  LinkageTypes.WeakODRLinkage
    LINKAGE_APPENDING               =  LinkageTypes.AppendingLinkage
    LINKAGE_INTERNAL                =  LinkageTypes.InternalLinkage
    LINKAGE_PRIVATE                 =  LinkageTypes.PrivateLinkage
    LINKAGE_DLLIMPORT               =  LinkageTypes.DLLImportLinkage
    LINKAGE_DLLEXPORT               =  LinkageTypes.DLLExportLinkage
    LINKAGE_EXTERNAL_WEAK           =  LinkageTypes.ExternalWeakLinkage
    LINKAGE_COMMON                  =  LinkageTypes.CommonLinkage
    LINKAGE_LINKER_PRIVATE          =  LinkageTypes.LinkerPrivateLinkage
    LINKAGE_LINKER_PRIVATE_WEAK     =  LinkageTypes.LinkerPrivateWeakLinkage

LinkageEnum.declare()

# visibility (see llvm/GlobalValue.h)
class VisibilityEnum(Enum):
    prefix = 'VISIBILITY_'

    VISIBILITY_DEFAULT   = api.llvm.GlobalValue.VisibilityTypes.DefaultVisibility
    VISIBILITY_HIDDEN    = api.llvm.GlobalValue.VisibilityTypes.HiddenVisibility
    VISIBILITY_PROTECTED = api.llvm.GlobalValue.VisibilityTypes.ProtectedVisibility

VisibilityEnum.declare()

# parameter attributes
#      LLVM 3.2 llvm::Attributes::AttrVal (see llvm/Attributes.h)
#      LLVM 3.3 llvm::Attribute::AttrKind (see llvm/Attributes.h)
class AttrEnum(Enum):
    prefix = 'ATTR_'

    if llvm.version >= (3, 3):
        AttrVal = api.llvm.Attribute.AttrKind
    else:
        AttrVal = api.llvm.Attributes.AttrVal

    ATTR_NONE               = AttrVal.None_
    ATTR_ZEXT               = AttrVal.ZExt
    ATTR_SEXT               = AttrVal.SExt
    ATTR_NO_RETURN          = AttrVal.NoReturn
    ATTR_IN_REG             = AttrVal.InReg
    ATTR_STRUCT_RET         = AttrVal.StructRet
    ATTR_NO_UNWIND          = AttrVal.NoUnwind
    ATTR_NO_ALIAS           = AttrVal.NoAlias
    ATTR_BY_VAL             = AttrVal.ByVal
    ATTR_NEST               = AttrVal.Nest
    ATTR_READ_NONE          = AttrVal.ReadNone
    ATTR_READONLY           = AttrVal.ReadOnly
    ATTR_NO_INLINE          = AttrVal.NoInline
    ATTR_ALWAYS_INLINE      = AttrVal.AlwaysInline
    ATTR_OPTIMIZE_FOR_SIZE  = AttrVal.OptimizeForSize
    ATTR_STACK_PROTECT      = AttrVal.StackProtect
    ATTR_STACK_PROTECT_REQ  = AttrVal.StackProtectReq
    ATTR_ALIGNMENT          = AttrVal.Alignment
    ATTR_NO_CAPTURE         = AttrVal.NoCapture
    ATTR_NO_REDZONE         = AttrVal.NoRedZone
    ATTR_NO_IMPLICIT_FLOAT  = AttrVal.NoImplicitFloat
    ATTR_NAKED              = AttrVal.Naked
    ATTR_INLINE_HINT        = AttrVal.InlineHint
    ATTR_STACK_ALIGNMENT    = AttrVal.StackAlignment

AttrEnum.declare()

class Module(llvm.Wrapper):
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
    __cache = weakref.WeakValueDictionary()

    def __new__(cls, ptr):
        cached = cls.__cache.get(ptr)
        if cached:
            return cached
        obj = object.__new__(cls)
        cls.__cache[ptr] = obj
        return obj

    @staticmethod
    def new(id):
        """Create a new Module instance.

        Creates an instance of Module, having the id `id'.
        """
        context = api.llvm.getGlobalContext()
        m = api.llvm.Module.new(id, context)
        return Module(m)

    @staticmethod
    def from_bitcode(fileobj_or_str):
        """Create a Module instance from the contents of a bitcode
        file.

        fileobj_or_str -- takes a file-like object or string that contains
        a module represented in bitcode.
        """
        if isinstance(fileobj_or_str, str):
            bc = fileobj_or_str
        else:
            bc = fileobj_or_str.read()
        errbuf = BytesIO()
        context = api.llvm.getGlobalContext()
        m = api.llvm.ParseBitCodeFile(bc, context, errbuf)
        if not m:
            raise Exception(errbuf.getvalue())
        errbuf.close()
        return Module(m)


    @staticmethod
    def from_assembly(fileobj_or_str):
        """Create a Module instance from the contents of an LLVM
        assembly (.ll) file.


        fileobj_or_str -- takes a file-like object or string that contains
        a module represented in llvm-ir assembly.
        """
        if isinstance(fileobj_or_str, str):
            ir = fileobj_or_str
        else:
            ir = fileobj_or_str.read()
        errbuf = BytesIO()
        context = api.llvm.getGlobalContext()
        m = api.llvm.ParseAssemblyString(ir, None, api.llvm.SMDiagnostic.new(),
                                         context)
        errbuf.close()
        return Module(m)

    def __str__(self):
        """Text representation of a module.

            Returns the textual representation (`llvm assembly') of the
            module. Use it like this:

            ll = str(module_obj)
            print module_obj     # same as `print ll'
            """
        return str(self._ptr)

    def __eq__(self, rhs):
        assert isinstance(rhs, Module), type(rhs)
        if isinstance(rhs, Module):
            return str(self) == str(rhs)
        else:
            return False

    def __ne__(self, rhs):
        return not (self == rhs)


    def _get_target(self):
        return self._ptr.getTargetTriple()

    def _set_target(self, value):
        return self._ptr.setTargetTriple(value)

    target = property(_get_target, _set_target,
              doc="The target triple string describing the target host.")


    def _get_data_layout(self):
        return self._ptr.getDataLayout()

    def _set_data_layout(self, value):
        return self._ptr.setDataLayout(value)

    data_layout = property(_get_data_layout, _set_data_layout,
           doc = """The data layout string for the module's target platform.

               The data layout strings is an encoded representation of
               the type sizes and alignments expected by this module.
               """
           )

    @property
    def pointer_size(self):
        return self._ptr.getPointerSize()

    def link_in(self, other, preserve=False):
        """Link the `other' module into this one.

        The `other' module is linked into this one such that types,
        global variables, function, etc. are matched and resolved.

        The `other' module is no longer valid after this method is
        invoked, all refs to it should be dropped.

        In the future, this API might be replaced with a full-fledged
        Linker class.
        """
        assert isinstance(other, Module)
        enum_mode = api.llvm.Linker.LinkerMode
        mode = enum_mode.PreserveSource if preserve else enum_mode.DestroySource

        with contextlib.closing(BytesIO()) as errmsg:
            failed = api.llvm.Linker.LinkModules(self._ptr,
                                                 other._ptr,
                                                 mode,
                                                 errmsg)
            if failed:
                raise llvm.LLVMException(errmsg.getvalue())

    def get_type_named(self, name):
        typ = self._ptr.getTypeByName(name)
        if typ:
            return StructType(typ)

    def add_global_variable(self, ty, name, addrspace=0):
        """Add a global variable of given type with given name."""
        external = api.llvm.GlobalVariable.LinkageTypes.ExternalLinkage
        notthreadlocal = api.llvm.GlobalVariable.ThreadLocalMode.NotThreadLocal
        init = None
        insertbefore = None
        ptr = api.llvm.GlobalVariable.new(self._ptr,
                                     ty._ptr,
                                     False,
                                     external,
                                     init,
                                     name,
                                     insertbefore,
                                     notthreadlocal,
                                     addrspace)
        return _make_value(ptr)

    def get_global_variable_named(self, name):
        """Return a GlobalVariable object for the given name."""
        ptr = self._ptr.getNamedGlobal(name)
        if ptr is None:
            raise llvm.LLVMException("No global named: %s" % name)
        return _make_value(ptr)

    @property
    def global_variables(self):
        return list(map(_make_value, self._ptr.list_globals()))

    def add_function(self, ty, name):
        """Add a function of given type with given name."""
        return Function.new(self, ty, name)
#        fn = self.get_function_named(name)
#        if fn is not None:
#            raise llvm.LLVMException("Duplicated function %s" % name)
#        return self.get_or_insert_function(ty, name)

    def get_function_named(self, name):
        """Return a Function object representing function with given name."""
        return Function.get(self, name)
#        fn = self._ptr.getFunction(name)
#        if fn is not None:
#            return _make_value(fn)

    def get_or_insert_function(self, ty, name):
        """Like get_function_named(), but does add_function() first, if
           function is not present."""
        return Function.get_or_insert(self, ty, name)
#        constant = self._ptr.getOrInsertFunction(name, ty._ptr)
#        try:
#            fn = constant._downcast(api.llvm.Function)
#        except ValueError:
#            # bitcasted to function type
#            return _make_value(constant)
#        else:
#            return _make_value(fn)

    @property
    def functions(self):
        """All functions in this module."""
        return list(map(_make_value, self._ptr.list_functions()))

    def verify(self):
        """Verify module.

            Checks module for errors. Raises `llvm.LLVMException' on any
            error."""
        action = api.llvm.VerifierFailureAction.ReturnStatusAction
        errio = BytesIO()
        broken = api.llvm.verifyModule(self._ptr, action, errio)
        if broken:
            raise llvm.LLVMException(errio.getvalue())

    def to_bitcode(self, fileobj=None):
        """Write bitcode representation of module to given file-like
        object.

        fileobj -- A file-like object to where the bitcode is written.
        If it is None, the bitcode is returned.

        Return value -- Returns None if fileobj is not None.
        Otherwise, return the bitcode as a bytestring.
        """
        ret = False
        if fileobj is None:
            ret = True
            fileobj = BytesIO()
        api.llvm.WriteBitcodeToFile(self._ptr, fileobj)
        if ret:
            return fileobj.getvalue()

    def _get_id(self):
        return self._ptr.getModuleIdentifier()

    def _set_id(self, string):
        self._ptr.setModuleIdentifier(string)

    id = property(_get_id, _set_id)

    def _to_native_something(self, fileobj, cgft):

        cgft = api.llvm.TargetMachine.CodeGenFileType.CGFT_AssemblyFile
        cgft = api.llvm.TargetMachine.CodeGenFileType.CGFT_ObjectFile

        from llvm.ee import TargetMachine
        from llvm.passes import PassManager
        from llvmpy import extra
        tm = TargetMachine.new()._ptr
        pm = PassManager.new()._ptr
        formatted
        failed = tm.addPassesToEmitFile(pm, fileobj, cgft, False)

        if failed:
            raise llvm.LLVMException("Failed to write native object file")
        if ret:
            return fileobj.getvalue()


    def to_native_object(self, fileobj=None):
        '''Outputs the byte string of the module as native object code

        If a fileobj is given, the output is written to it;
        Otherwise, the output is returned
        '''
        ret = False
        if fileobj is None:
            ret = True
            fileobj = BytesIO()
        from llvm.ee import TargetMachine
        tm = TargetMachine.new()
        fileobj.write(tm.emit_object(self))
        if ret:
            return fileobj.getvalue()


    def to_native_assembly(self, fileobj=None):
        '''Outputs the byte string of the module as native assembly code

        If a fileobj is given, the output is written to it;
        Otherwise, the output is returned
        '''
        ret = False
        if fileobj is None:
            ret = True
            fileobj = StringIO()
        from llvm.ee import TargetMachine
        tm = TargetMachine.new()
        asm = tm.emit_assembly(self)
        fileobj.write(asm)
        if ret:
            return fileobj.getvalue()


    def get_or_insert_named_metadata(self, name):
        return NamedMetaData(self._ptr.getOrInsertNamedMetadata(name))

    def get_named_metadata(self, name):
        md = self._ptr.getNamedMetadata(name)
        if md:
            return NamedMetaData(md)

    def clone(self):
        return Module(api.llvm.CloneModule(self._ptr))

class Type(llvm.Wrapper):
    """Represents a type, like a 32-bit integer or an 80-bit x86 float.

    Use one of the static methods to create an instance. Example:
    ty = Type.double()
    """
    _type_ = api.llvm.Type

    def __init__(self, ptr):
        ptr = ptr._downcast(type(self)._type_)
        super(Type, self).__init__(ptr)

    @property
    def kind(self):
        return self._ptr.getTypeID()

    @staticmethod
    def int(bits=32):
        """Create an integer type having the given bit width."""
        context = api.llvm.getGlobalContext()
        ptr = api.llvm.Type.getIntNTy(context, bits)
        return Type(ptr)

    @staticmethod
    def float():
        """Create a 32-bit floating point type."""
        context = api.llvm.getGlobalContext()
        ptr = api.llvm.Type.getFloatTy(context)
        return Type(ptr)

    @staticmethod
    def double():
        """Create a 64-bit floating point type."""
        context = api.llvm.getGlobalContext()
        ptr = api.llvm.Type.getDoubleTy(context)
        return Type(ptr)

    @staticmethod
    def x86_fp80():
        """Create a 80-bit x86 floating point type."""
        context = api.llvm.getGlobalContext()
        ptr = api.llvm.Type.getX86_FP80Ty(context)
        return Type(ptr)

    @staticmethod
    def fp128():
        """Create a 128-bit floating point type (with 112-bit
            mantissa)."""
        context = api.llvm.getGlobalContext()
        ptr = api.llvm.Type.getFP128Ty(context)
        return Type(ptr)

    @staticmethod
    def ppc_fp128():
        """Create a 128-bit floating point type (two 64-bits)."""
        context = api.llvm.getGlobalContext()
        ptr = api.llvm.Type.getPPC_FP128Ty(context)
        return Type(ptr)


    @staticmethod
    def function(return_ty, param_tys, var_arg=False):
        """Create a function type.

        Creates a function type that returns a value of type
        `return_ty', takes arguments of types as given in the iterable
        `param_tys'. Set `var_arg' to True (default is False) for a
        variadic function."""
        ptr = api.llvm.FunctionType.get(return_ty._ptr,
                                   llvm._extract_ptrs(param_tys),
                                   var_arg)
        return FunctionType(ptr)

    @staticmethod
    def opaque(name):
        """Create a opaque StructType"""
        context = api.llvm.getGlobalContext()
        if not name:
            raise llvm.LLVMException("Opaque type must have a non-empty name")
        ptr = api.llvm.StructType.create(context, name)
        return StructType(ptr)

    @staticmethod
    def struct(element_tys, name=''): # not packed
        """Create a (unpacked) structure type.

        Creates a structure type with elements of types as given in the
        iterable `element_tys'. This method creates a unpacked
        structure. For a packed one, use the packed_struct() method.

        If name is not '', creates a identified type;
        otherwise, creates a literal type."""
        context = api.llvm.getGlobalContext()
        is_packed = False
        if name:
            ptr = api.llvm.StructType.create(context, name)
            ptr.setBody(llvm._extract_ptrs(element_tys), is_packed)
        else:
            ptr = api.llvm.StructType.get(context,
                                          llvm._extract_ptrs(element_tys),
                                          is_packed)


        return StructType(ptr)

    @staticmethod
    def packed_struct(element_tys, name=''):
        """Create a (packed) structure type.

        Creates a structure type with elements of types as given in the
        iterable `element_tys'. This method creates a packed
        structure. For an unpacked one, use the struct() method.

        If name is not '', creates a identified type;
        otherwise, creates a literal type."""
        context = api.llvm.getGlobalContext()
        is_packed = True
        ptr = api.llvm.StructType.create(context, name)
        ptr.setBody(llvm._extract_ptrs(element_tys), is_packed)
        return StructType(ptr)

    @staticmethod
    def array(element_ty, count):
        """Create an array type.

        Creates a type for an array of elements of type `element_ty',
        having 'count' elements."""
        ptr = api.llvm.ArrayType.get(element_ty._ptr, count)
        return ArrayType(ptr)

    @staticmethod
    def pointer(pointee_ty, addr_space=0):
        """Create a pointer type.

        Creates a pointer type, which can point to values of type
        `pointee_ty', in the address space `addr_space'."""
        ptr = api.llvm.PointerType.get(pointee_ty._ptr, addr_space)
        return PointerType(ptr)

    @staticmethod
    def vector(element_ty, count):
        """Create a vector type.

        Creates a type for a vector of elements of type `element_ty',
        having `count' elements."""
        ptr = api.llvm.VectorType.get(element_ty._ptr, count)
        return VectorType(ptr)

    @staticmethod
    def void():
        """Create a void type.

        Represents the `void' type."""
        context = api.llvm.getGlobalContext()
        ptr = api.llvm.Type.getVoidTy(context)
        return Type(ptr)

    @staticmethod
    def label():
        """Create a label type."""
        context = api.llvm.getGlobalContext()
        ptr = api.llvm.Type.getLabelTy(context)
        return Type(ptr)

    def __new__(cls, ptr):
        tyid = ptr.getTypeID()

        idmap = {
            TYPE_HALF:      IntegerType,
            TYPE_INTEGER:   IntegerType,
            TYPE_FUNCTION:  FunctionType,
            TYPE_STRUCT:    StructType,
            TYPE_ARRAY:     ArrayType,
            TYPE_POINTER:   PointerType,
            TYPE_VECTOR:    VectorType,
        }

        try:
            newcls = idmap[tyid]
        except KeyError:
            newcls = Type
        obj = llvm.Wrapper.__new__(newcls)
        return obj

    def __str__(self):
        return str(self._ptr)

    def __hash__(self):
        return hash(self._ptr)

    def __eq__(self, rhs):
        return self._ptr is rhs._ptr

    def __ne__(self, rhs):
        return not (self == rhs)

class IntegerType(Type):
    """Represents an integer type."""
    _type_ = api.llvm.IntegerType

    @property
    def width(self):
        """The width of the integer type, in bits."""
        return self._ptr.getIntegerBitWidth()

class FunctionType(Type):
    """Represents a function type."""
    _type_ = api.llvm.FunctionType

    @property
    def return_type(self):
        """The type of the value returned by this function."""
        return Type(self._ptr.getReturnType())

    @property
    def vararg(self):
        """True if this function is variadic."""
        return self._ptr.isVarArg()

    @property
    def args(self):
        """An iterable that yields Type objects, representing the types of the
            arguments accepted by this function, in order."""
        return [Type(self._ptr.getParamType(i)) for i in range(self.arg_count)]

    @property
    def arg_count(self):
        """Number of arguments accepted by this function.

            Same as len(obj.args), but faster."""
        return self._ptr.getNumParams()


class StructType(Type):
    """Represents a structure type."""
    _type_ = api.llvm.StructType

    @property
    def element_count(self):
        """Number of elements (members) in the structure.

            Same as len(obj.elements), but faster."""
        return self._ptr.getNumElements()

    @property
    def elements(self):
        """An iterable that yields Type objects, representing the types of the
            elements (members) of the structure, in order."""
        return [Type(self._ptr.getElementType(i))
                for i in range(self._ptr.getNumElements())]

    def set_body(self, elems, packed=False):
        """Filled the body of a opaque type.
            """
        # check
        if not self.is_opaque:
            raise llvm.LLVMException("Body is already defined.")

        self._ptr.setBody(llvm._extract_ptrs(elems), packed)

    @property
    def packed(self):
        """True if the structure is packed, False otherwise."""
        return self._ptr.isPacked()

    def _set_name(self, name):
        self._ptr.setName(name)

    def _get_name(self):
        if self._ptr.isLiteral():
           return ""
        else:
           return self._ptr.getName()

    name = property(_get_name, _set_name)

    @property
    def is_literal(self):
        return self._ptr.isLiteral()

    @property
    def is_identified(self):
        return not self.is_literal

    @property
    def is_opaque(self):
        return self._ptr.isOpaque()

    def is_layout_identical(self, other):
        return self._ptr.isLayoutIdentical(other._ptr)

class ArrayType(Type):
    """Represents an array type."""
    _type_ = api.llvm.ArrayType

    @property
    def element(self):
        return Type(self._ptr.getArrayElementType())

    @property
    def count(self):
        return self._ptr.getNumElements()

class PointerType(Type):
    _type_ = api.llvm.PointerType

    @property
    def pointee(self):
        return Type(self._ptr.getPointerElementType())

    @property
    def address_space(self):
        return self._ptr.getAddressSpace()

class VectorType(Type):
    _type_ = api.llvm.VectorType

    @property
    def element(self):
        return Type(self._ptr.getVectorElementType())

    @property
    def count(self):
        return self._ptr.getNumElements()

class Value(llvm.Wrapper):
    _type_ = api.llvm.Value

    def __init__(self, builder, ptr):
        assert builder is _ValueFactory

        if type(self._type_) is type:
            if isinstance(ptr, self._type_): # is not downcast
                casted = ptr
            else:
                casted = ptr._downcast(self._type_)
        else:
            try:
                for ty in self._type_:
                    if isinstance(ptr, ty): # is not downcast
                        casted = ptr
                    else:
                        try:
                            casted = ptr._downcast(ty)
                        except ValueError:
                            pass
                        else:
                            break
                else:
                    casted = ptr
            except TypeError:
                casted = ptr
        super(Value, self).__init__(casted)

    def __str__(self):
        return str(self._ptr)

    def __hash__(self):
        return hash(self._ptr)

    def __eq__(self, rhs):
        if isinstance(rhs, Value):
            return str(self) == str(rhs)
        else:
            return False

    def __ne__(self, rhs):
        return not self == rhs

    def _get_name(self):
        return self._ptr.getName()

    def _set_name(self, value):
        return self._ptr.setName(value)

    name = property(_get_name, _set_name)

    @property
    def value_id(self):
        return self._ptr.getValueID()

    @property
    def type(self):
        return Type(self._ptr.getType())

    @property
    def use_count(self):
        return self._ptr.getNumUses()

    @property
    def uses(self):
        return list(map(_make_value, self._ptr.list_use()))

class User(Value):
    _type_ = api.llvm.User

    @property
    def operand_count(self):
        return self._ptr.getNumOperands()

    @property
    def operands(self):
        """Yields operands of this instruction."""
        return [_make_value(self._ptr.getOperand(i))
                for i in range(self.operand_count)]


class Constant(User):
    _type_ = api.llvm.Constant

    @staticmethod
    def null(ty):
        return _make_value(api.llvm.Constant.getNullValue(ty._ptr))

    @staticmethod
    def all_ones(ty):
        return _make_value(api.llvm.Constant.getAllOnesValue(ty._ptr))

    @staticmethod
    def undef(ty):
        return _make_value(api.llvm.UndefValue.get(ty._ptr))

    @staticmethod
    def int(ty, value):
        return _make_value(api.llvm.ConstantInt.get(ty._ptr, int(value), False))

    @staticmethod
    def int_signextend(ty, value):
        return _make_value(api.llvm.ConstantInt.get(ty._ptr, int(value), True))

    @staticmethod
    def real(ty, value):
        return _make_value(api.llvm.ConstantFP.get(ty._ptr, float(value)))

    @staticmethod
    def string(strval): # dont_null_terminate=True
        cxt = api.llvm.getGlobalContext()
        return _make_value(api.llvm.ConstantDataArray.getString(cxt, strval, False))

    @staticmethod
    def stringz(strval): # dont_null_terminate=False
        cxt = api.llvm.getGlobalContext()
        return _make_value(api.llvm.ConstantDataArray.getString(cxt, strval, True))

    @staticmethod
    def array(ty, consts):
        aryty = Type.array(ty, len(consts))
        return _make_value(api.llvm.ConstantArray.get(aryty._ptr,
                                                      llvm._extract_ptrs(consts)))

    @staticmethod
    def struct(consts): # not packed
        return _make_value(api.llvm.ConstantStruct.getAnon(llvm._extract_ptrs(consts),
                                                False))

    @staticmethod
    def packed_struct(consts):
         return _make_value(api.llvm.ConstantStruct.getAnon(llvm._extract_ptrs(consts),
                                                 False))

    @staticmethod
    def vector(consts):
        return _make_value(api.llvm.ConstantVector.get(llvm._extract_ptrs(consts)))

    @staticmethod
    def sizeof(ty):
        return _make_value(api.llvm.ConstantExpr.getSizeOf(ty._ptr))

    def neg(self):
        return _make_value(api.llvm.ConstantExpr.getNeg(self._ptr))

    def not_(self):
        return _make_value(api.llvm.ConstantExpr.getNot(self._ptr))

    def add(self, rhs):
        return _make_value(api.llvm.ConstantExpr.getAdd(self._ptr, rhs._ptr))

    def fadd(self, rhs):
        return _make_value(api.llvm.ConstantExpr.getFAdd(self._ptr, rhs._ptr))

    def sub(self, rhs):
        return _make_value(api.llvm.ConstantExpr.getSub(self._ptr, rhs._ptr))

    def fsub(self, rhs):
        return _make_value(api.llvm.ConstantExpr.getFSub(self._ptr, rhs._ptr))

    def mul(self, rhs):
        return _make_value(api.llvm.ConstantExpr.getMul(self._ptr, rhs._ptr))

    def fmul(self, rhs):
        return _make_value(api.llvm.ConstantExpr.getFMul(self._ptr, rhs._ptr))

    def udiv(self, rhs):
        return _make_value(api.llvm.ConstantExpr.getUDiv(self._ptr, rhs._ptr))

    def sdiv(self, rhs):
        return _make_value(api.llvm.ConstantExpr.getSDiv(self._ptr, rhs._ptr))

    def fdiv(self, rhs):
        return _make_value(api.llvm.ConstantExpr.getFDiv(self._ptr, rhs._ptr))

    def urem(self, rhs):
        return _make_value(api.llvm.ConstantExpr.getURem(self._ptr, rhs._ptr))

    def srem(self, rhs):
        return _make_value(api.llvm.ConstantExpr.getSRem(self._ptr, rhs._ptr))

    def frem(self, rhs):
        return _make_value(api.llvm.ConstantExpr.getFRem(self._ptr, rhs._ptr))

    def and_(self, rhs):
        return _make_value(api.llvm.ConstantExpr.getAnd(self._ptr, rhs._ptr))

    def or_(self, rhs):
        return _make_value(api.llvm.ConstantExpr.getOr(self._ptr, rhs._ptr))

    def xor(self, rhs):
        return _make_value(api.llvm.ConstantExpr.getXor(self._ptr, rhs._ptr))

    def icmp(self, int_pred, rhs):
        return _make_value(api.llvm.ConstantExpr.getICmp(int_pred, self._ptr, rhs._ptr))

    def fcmp(self, real_pred, rhs):
        return _make_value(api.llvm.ConstantExpr.getFCmp(real_pred, self._ptr, rhs._ptr))

    def shl(self, rhs):
        return _make_value(api.llvm.ConstantExpr.getShl(self._ptr, rhs._ptr))

    def lshr(self, rhs):
        return _make_value(api.llvm.ConstantExpr.getLShr(self._ptr, rhs._ptr))

    def ashr(self, rhs):
        return _make_value(api.llvm.ConstantExpr.getAShr(self._ptr, rhs._ptr))

    def gep(self, indices):
        indices = llvm._extract_ptrs(indices)
        return _make_value(api.llvm.ConstantExpr.getGetElementPtr(self._ptr, indices))

    def trunc(self, ty):
        return _make_value(api.llvm.ConstantExpr.getTrunc(self._ptr, ty._ptr))

    def sext(self, ty):
        return _make_value(api.llvm.ConstantExpr.getSExt(self._ptr, ty._ptr))

    def zext(self, ty):
        return _make_value(api.llvm.ConstantExpr.getZExt(self._ptr, ty._ptr))

    def fptrunc(self, ty):
        return _make_value(api.llvm.ConstantExpr.getFPTrunc(self._ptr, ty._ptr))

    def fpext(self, ty):
        return _make_value(api.llvm.ConstantExpr.getFPExtend(self._ptr, ty._ptr))

    def uitofp(self, ty):
        return _make_value(api.llvm.ConstantExpr.getUIToFP(self._ptr, ty._ptr))

    def sitofp(self, ty):
        return _make_value(api.llvm.ConstantExpr.getSIToFP(self._ptr, ty._ptr))

    def fptoui(self, ty):
        return _make_value(api.llvm.ConstantExpr.getFPToUI(self._ptr, ty._ptr))

    def fptosi(self, ty):
        return _make_value(api.llvm.ConstantExpr.getFPToSI(self._ptr, ty._ptr))

    def ptrtoint(self, ty):
        return _make_value(api.llvm.ConstantExpr.getPtrToInt(self._ptr, ty._ptr))

    def inttoptr(self, ty):
        return _make_value(api.llvm.ConstantExpr.getIntToPtr(self._ptr, ty._ptr))

    def bitcast(self, ty):
        return _make_value(api.llvm.ConstantExpr.getBitCast(self._ptr, ty._ptr))

    def select(self, true_const, false_const):
        return _make_value(api.llvm.ConstantExpr.getSelect(self._ptr,
                                                true_const._ptr,
                                                false_const._ptr))

    def extract_element(self, index): # note: self must be a _vector_ constant
        return _make_value(api.llvm.ConstantExpr.getExtractElement(self._ptr, index._ptr))

    def insert_element(self, value, index):
        return _make_value(api.llvm.ConstantExpr.getExtractElement(self._ptr,
                                                        value._ptr,
                                                        index._ptr))

    def shuffle_vector(self, vector_b, mask):
        return _make_value(api.llvm.ConstantExpr.getShuffleVector(self._ptr,
                                                       vector_b._ptr,
                                                       mask._ptr))

class ConstantExpr(Constant):
    _type_ = api.llvm.ConstantExpr

    @property
    def opcode(self):
        return self._ptr.getOpcode()

    @property
    def opcode_name(self):
        return self._ptr.getOpcodeName()

class ConstantAggregateZero(Constant):
    pass


class ConstantDataArray(Constant):
    pass


class ConstantDataVector(Constant):
    pass


class ConstantInt(Constant):
    _type_ = api.llvm.ConstantInt

    @property
    def z_ext_value(self):
        '''Obtain the zero extended value for an integer constant value.'''
        # Warning: assertion failure when value does not fit in 64 bits
        return self._ptr.getZExtValue()

    @property
    def s_ext_value(self):
        '''Obtain the sign extended value for an integer constant value.'''
        # Warning: assertion failure when value does not fit in 64 bits
        return self._ptr.getSExtValue()


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
    _type_ = api.llvm.GlobalValue

    def _get_linkage(self):
        return self._ptr.getLinkage()

    def _set_linkage(self, value):
        self._ptr.setLinkage(value)

    linkage = property(_get_linkage, _set_linkage)

    def _get_section(self):
        return self._ptr.getSection()

    def _set_section(self, value):
        return self._ptr.setSection(value)

    section = property(_get_section, _set_section)

    def _get_visibility(self):
        return self._ptr.getVisibility()

    def _set_visibility(self, value):
        return self._ptr.setVisibility(value)

    visibility = property(_get_visibility, _set_visibility)

    def _get_alignment(self):
        return self._ptr.getAlignment()

    def _set_alignment(self, value):
        return self._ptr.setAlignment(value)

    alignment = property(_get_alignment, _set_alignment)

    @property
    def is_declaration(self):
        return self._ptr.isDeclaration()

    @property
    def module(self):
        return Module(self._ptr.getParent())



class GlobalVariable(GlobalValue):
    _type_ = api.llvm.GlobalVariable

    @staticmethod
    def new(module, ty, name, addrspace=0):
        linkage = api.llvm.GlobalValue.LinkageTypes
        external_linkage = linkage.ExternalLinkage
        tlmode = api.llvm.GlobalVariable.ThreadLocalMode
        not_threadlocal = tlmode.NotThreadLocal
        gv = api.llvm.GlobalVariable.new(module._ptr,
                                     ty._ptr,
                                     False, # is constant
                                     external_linkage,
                                     None, # initializer
                                     name,
                                     None, # insert before
                                     not_threadlocal,
                                     addrspace)
        return _make_value(gv)

    @staticmethod
    def get(module, name):
        gv = _make_value(module._ptr.getNamedGlobal(name))
        if not gv:
            llvm.LLVMException("no global named `%s`" % name)
        return gv

    def delete(self):
        _ValueFactory.delete(self._ptr)
        self._ptr.eraseFromParent()

    def _get_initializer(self):
        if not self._ptr.hasInitializer():
            return None
        return _make_value(self._ptr.getInitializer())

    def _set_initializer(self, const):
        self._ptr.setInitializer(const._ptr)

    def _del_initializer(self):
        self._ptr.setInitializer(None)

    initializer = property(_get_initializer, _set_initializer)

    def _get_is_global_constant(self):
        return self._ptr.isConstant()

    def _set_is_global_constant(self, value):
        self._ptr.setConstant(value)

    global_constant = property(_get_is_global_constant,
                               _set_is_global_constant)

    def _get_thread_local(self):
        return self._ptr.isThreadLocal()

    def _set_thread_local(self, value):
        return self._ptr.setThreadLocal(value)

    thread_local = property(_get_thread_local, _set_thread_local)

class Argument(Value):
    _type_ = api.llvm.Argument
    _valid_attrs = frozenset([ATTR_BY_VAL, ATTR_NEST, ATTR_NO_ALIAS,
                              ATTR_NO_CAPTURE, ATTR_STRUCT_RET])

    if llvm.version >= (3, 3):
        def add_attribute(self, attr):
            context = api.llvm.getGlobalContext()
            attrbldr = api.llvm.AttrBuilder.new()
            attrbldr.addAttribute(attr)
            attrs = api.llvm.AttributeSet.get(context, 0, attrbldr)
            self._ptr.addAttr(attrs)

            if attr not in self:
                raise ValueError("Attribute %r is not valid for arg %s" %
                                 (attr, self))

        def remove_attribute(self, attr):
            context = api.llvm.getGlobalContext()
            attrbldr = api.llvm.AttrBuilder.new()
            attrbldr.addAttribute(attr)
            attrs = api.llvm.AttributeSet.get(context, 0, attrbldr)
            self._ptr.removeAttr(attrs)

        def _set_alignment(self, align):
            context = api.llvm.getGlobalContext()
            attrbldr = api.llvm.AttrBuilder.new()
            attrbldr.addAlignmentAttr(align)
            attrs = api.llvm.AttributeSet.get(context, 0, attrbldr)
            self._ptr.addAttr(attrs)
    else:
        def add_attribute(self, attr):
            context = api.llvm.getGlobalContext()
            attrbldr = api.llvm.AttrBuilder.new()
            attrbldr.addAttribute(attr)
            attrs = api.llvm.Attributes.get(context, attrbldr)
            self._ptr.addAttr(attrs)
            if attr not in self:
                raise ValueError("Attribute %r is not valid for arg %s" %
                                 (attr, self))

        def remove_attribute(self, attr):
            context = api.llvm.getGlobalContext()
            attrbldr = api.llvm.AttrBuilder.new()
            attrbldr.addAttribute(attr)
            attrs = api.llvm.Attributes.get(context, attrbldr)
            self._ptr.removeAttr(attrs)

        def _set_alignment(self, align):
            context = api.llvm.getGlobalContext()
            attrbldr = api.llvm.AttrBuilder.new()
            attrbldr.addAlignmentAttr(align)
            attrs = api.llvm.Attributes.get(context, attrbldr)
            self._ptr.addAttr(attrs)

    def _get_alignment(self):
        return self._ptr.getParamAlignment()

    alignment = property(_get_alignment,
                         _set_alignment)

    @property
    def attributes(self):
        '''Returns a set of defined attributes.
        '''
        return set(attr for attr in self._valid_attrs if attr in self)

    def __contains__(self, attr):
        if attr == ATTR_BY_VAL:
            return self.has_by_val()
        elif attr == ATTR_NEST:
            return self.has_nest()
        elif attr == ATTR_NO_ALIAS:
            return self.has_no_alias()
        elif attr == ATTR_NO_CAPTURE:
            return self.has_no_capture()
        elif attr == ATTR_STRUCT_RET:
            return self.has_struct_ret()
        else:
            raise ValueError('invalid attribute for argument')

    @property
    def arg_no(self):
        return self._ptr.getArgNo()

    def has_by_val(self):
        return self._ptr.hasByValAttr()

    def has_nest(self):
        return self._ptr.hasNestAttr()

    def has_no_alias(self):
        return self._ptr.hasNoAliasAttr()

    def has_no_capture(self):
        return self._ptr.hasNoCaptureAttr()

    def has_struct_ret(self):
        return self._ptr.hasStructRetAttr()

class Function(GlobalValue):
    _type_ = api.llvm.Function

    @staticmethod
    def new(module, func_ty, name):
        try:
            fn = Function.get(module, name)
        except llvm.LLVMException:
            return Function.get_or_insert(module, func_ty, name)
        else:
            raise llvm.LLVMException("Duplicated function %s" % name)


    @staticmethod
    def get_or_insert(module, func_ty, name):
        constant = module._ptr.getOrInsertFunction(name, func_ty._ptr)
        try:
            fn = constant._downcast(api.llvm.Function)
        except ValueError:
            # bitcasted to function type
            return _make_value(constant)
        else:
            return _make_value(fn)

    @staticmethod
    def get(module, name):
        fn = module._ptr.getFunction(name)
        if fn is None:
            raise llvm.LLVMException("no function named `%s`" % name)
        else:
            return _make_value(fn)

    @staticmethod
    def intrinsic(module, intrinsic_id, types):
        fn = api.llvm.Intrinsic.getDeclaration(module._ptr,
                                               intrinsic_id,
                                               llvm._extract_ptrs(types))
        return _make_value(fn)

    def delete(self):
        _ValueFactory.delete(self._ptr)
        self._ptr.eraseFromParent()

    @property
    def intrinsic_id(self):
        self._ptr.getIntrinsicID()

    def _get_cc(self):
        return self._ptr.getCallingConv()

    def _set_cc(self, value):
        self._ptr.setCallingConv(value)

    calling_convention = property(_get_cc, _set_cc)

    def _get_coll(self):
        return self._ptr.getGC()

    def _set_coll(self, value):
        return self._ptr.setGC(value)

    collector = property(_get_coll, _set_coll)

    # the nounwind attribute:
    def _get_does_not_throw(self):
        return self._ptr.doesNotThrow()

    def _set_does_not_throw(self,value):
        assert value
        self._ptr.setDoesNotThrow()

    does_not_throw = property(_get_does_not_throw, _set_does_not_throw)

    @property
    def args(self):
        args = self._ptr.getArgumentList()
        return list(map(_make_value, args))

    @property
    def basic_block_count(self):
        return len(self.basic_blocks)

    @property
    def entry_basic_block(self):
        assert self.basic_block_count
        return _make_value(self._ptr.getEntryBlock())

    def get_entry_basic_block(self):
        "Deprecated. Use entry_basic_block instead"
        return self.entry_basic_block

    def append_basic_block(self, name):
        context = api.llvm.getGlobalContext()
        bb = api.llvm.BasicBlock.Create(context, name, self._ptr, None)
        return _make_value(bb)

    @property
    def basic_blocks(self):
        return list(map(_make_value, self._ptr.getBasicBlockList()))

    def viewCFG(self):
        return self._ptr.viewCFG()

    def add_attribute(self, attr):
        self._ptr.addFnAttr(attr)

    def remove_attribute(self, attr):
        context = api.llvm.getGlobalContext()
        attrbldr = api.llvm.AttrBuilder.new()
        attrbldr.addAttribute(attr)
        if llvm.version >= (3, 3):
            attrs = api.llvm.Attribute.get(context, attrbldr)
        else:
            attrs = api.llvm.Attributes.get(context, attrbldr)
        self._ptr.removeFnAttr(attrs)

    def viewCFGOnly(self):
        return self._ptr.viewCFGOnly()

    def verify(self):
        # Although we're just asking LLVM to return the success or
        # failure, it appears to print result to stderr and abort.

        # Note: LLVM has a bug in preverifier that will always abort
        #       the process upon failure.
        actions = api.llvm.VerifierFailureAction
        broken = api.llvm.verifyFunction(self._ptr,
                                         actions.ReturnStatusAction)
        if broken:
            # If broken, then re-run to print the message
            api.llvm.verifyFunction(self._ptr, actions.PrintMessageAction)
            raise llvm.LLVMException("Function %s failed verification" %
                                     self.name)

#===----------------------------------------------------------------------===
# InlineAsm
#===----------------------------------------------------------------------===

class InlineAsm(Value):
    _type_ = api.llvm.InlineAsm

    @staticmethod
    def get(functype, asm, constrains, side_effect=False,
            align_stack=False, dialect=api.llvm.InlineAsm.AsmDialect.AD_ATT):
        ilasm = api.llvm.InlineAsm.get(functype._ptr, asm, constrains,
                                       side_effect, align_stack, dialect)
        return _make_value(ilasm)

#===----------------------------------------------------------------------===
# MetaData
#===----------------------------------------------------------------------===

class MetaData(Value):
    _type_ = api.llvm.MDNode

    @staticmethod
    def get(module, values):
        '''
        values -- must be an iterable of Constant or None. None is treated as "null".
        '''
        context = api.llvm.getGlobalContext()
        ptr = api.llvm.MDNode.get(context, llvm._extract_ptrs(values))
        return _make_value(ptr)

    @staticmethod
    def get_named_operands(module, name):
        namedmd = module.get_named_metadata(name)
        if not namedmd:
            return []
        return [_make_value(namedmd._ptr.getOperand(i))
                for i in range(namedmd._ptr.getNumOperands())]

    @staticmethod
    def add_named_operand(module, name, operand):
        namedmd = module.get_or_insert_named_metadata(name)._ptr
        namedmd.addOperand(operand._ptr)

    @property
    def operand_count(self):
        return self._ptr.getNumOperands()

    @property
    def operands(self):
        """Yields operands of this metadata."""
        res = []
        for i in range(self.operand_count):
            op = self._ptr.getOperand(i)
            if op is None:
                res.append(None)
            else:
                res.append(_make_value(op))
        return res

class MetaDataString(Value):
    _type_ = api.llvm.MDString

    @staticmethod
    def get(module, s):
        context = api.llvm.getGlobalContext()
        ptr = api.llvm.MDString.get(context, s)
        return _make_value(ptr)

    @property
    def string(self):
        '''Same as MDString::getString'''
        return self._ptr.getString()


class NamedMetaData(llvm.Wrapper):

    @staticmethod
    def get_or_insert(mod, name):
        return mod.get_or_insert_named_metadata(name)

    @staticmethod
    def get(mod, name):
        return mod.get_named_metadata(name)

    def delete(self):
        _ValueFactory.delete(self._ptr)
        self._ptr.eraseFromParent()

    @property
    def name(self):
        return self._ptr.getName()

    def __str__(self):
        return str(self._ptr)

    def add(self, operand):
        self._ptr.addOperand(operand._ptr)


#===----------------------------------------------------------------------===
# Instruction
#===----------------------------------------------------------------------===

class Instruction(User):
    _type_ = api.llvm.Instruction

    @property
    def basic_block(self):
        return _make_value(self._ptr.getParent())

    @property
    def is_terminator(self):
        return self._ptr.isTerminator()

    @property
    def is_binary_op(self):
        return self._ptr.isBinaryOp()

    @property
    def is_shift(self):
        return self._ptr.isShift()

    @property
    def is_cast(self):
        return self._ptr.isCast()

    @property
    def is_logical_shift(self):
        return self._ptr.isLogicalShift()

    @property
    def is_arithmetic_shift(self):
        return self._ptr.isArithmeticShift()

    @property
    def is_associative(self):
        return self._ptr.isAssociative()

    @property
    def is_commutative(self):
        return self._ptr.isCommutative()

    @property
    def is_volatile(self):
        """True if this is a volatile load or store."""
        if api.llvm.LoadInst.classof(self._ptr):
            return self._ptr._downcast(api.llvm.LoadInst).isVolatile()
        elif api.llvm.StoreInst.classof(self._ptr):
            return self._ptr._downcast(api.llvm.StoreInst).isVolatile()
        else:
            return False

    def set_volatile(self, flag):
        if api.llvm.LoadInst.classof(self._ptr):
            return self._ptr._downcast(api.llvm.LoadInst).setVolatile(flag)
        elif api.llvm.StoreInst.classof(self._ptr):
            return self._ptr._downcast(api.llvm.StoreInst).setVolatile(flag)
        else:
            return False

    def set_metadata(self, kind, metadata):
        self._ptr.setMetadata(kind, metadata._ptr)

    def has_metadata(self):
        return self._ptr.hasMetadata()

    def get_metadata(self, kind):
        return self._ptr.getMetadata(kind)

    @property
    def opcode(self):
        return self._ptr.getOpcode()

    @property
    def opcode_name(self):
        return self._ptr.getOpcodeName()

    def erase_from_parent(self):
        return self._ptr.eraseFromParent()

    def replace_all_uses_with(self, inst):
        self._ptr.replaceAllUsesWith(inst)


class CallOrInvokeInstruction(Instruction):
    _type_ = api.llvm.CallInst, api.llvm.InvokeInst

    def _get_cc(self):
        return self._ptr.getCallingConv()

    def _set_cc(self, value):
        return self._ptr.setCallingConv(value)

    calling_convention = property(_get_cc, _set_cc)

    def add_parameter_attribute(self, idx, attr):
        context = api.llvm.getGlobalContext()
        attrbldr = api.llvm.AttrBuilder.new()
        attrbldr.addAttribute(attr)
        if llvm.version >= (3, 3):
            attrs = api.llvm.Attribute.get(context, attrbldr)
        else:
            attrs = api.llvm.Attributes.get(context, attrbldr)

        self._ptr.addAttribute(idx, attrs)

    def remove_parameter_attribute(self, idx, attr):
        context = api.llvm.getGlobalContext()
        attrbldr = api.llvm.AttrBuilder.new()
        attrbldr.addAttribute(attr)
        if llvm.version >= (3, 3):
            attrs = api.llvm.Attribute.get(context, attrbldr)
        else:
            attrs = api.llvm.Attributes.get(context, attrbldr)

        self._ptr.removeAttribute(idx, attrs)

    def set_parameter_alignment(self, idx, align):
        context = api.llvm.getGlobalContext()
        attrbldr = api.llvm.AttrBuilder.new()
        attrbldr.addAlignmentAttr(align)
        if llvm.version >= (3, 3):
            attrs = api.llvm.Attribute.get(context, attrbldr)
        else:
            attrs = api.llvm.Attributes.get(context, attrbldr)

        self._ptr.addAttribute(idx, attrs)

    def _get_called_function(self):
        function = self._ptr.getCalledFunction()
        if function: # Return value can be None on indirect call/invoke
            return _make_value(function)

    def _set_called_function(self, function):
        self._ptr.setCalledFunction(function._ptr)

    called_function = property(_get_called_function, _set_called_function)


class PHINode(Instruction):
    _type_ = api.llvm.PHINode

    @property
    def incoming_count(self):
        return self._ptr.getNumIncomingValues()

    def add_incoming(self, value, block):
        self._ptr.addIncoming(value._ptr, block._ptr)

    def get_incoming_value(self, idx):
        return _make_value(self._ptr.getIncomingValue(idx))

    def get_incoming_block(self, idx):
        return _make_value(self._ptr.getIncomingBlock(idx))


class SwitchInstruction(Instruction):
    _type_ = api.llvm.SwitchInst

    def add_case(self, const, bblk):
        self._ptr.addCase(const._ptr, bblk._ptr)


class CompareInstruction(Instruction):
    _type_ = api.llvm.CmpInst

    @property
    def predicate(self):
        n = self._ptr.getPredicate()
        try:
            return ICMPEnum.get(n)
        except KeyError:
            return FCMPEnum.get(n)


#===----------------------------------------------------------------------===
# Basic block
#===----------------------------------------------------------------------===

class BasicBlock(Value):
    _type_ = api.llvm.BasicBlock

    def insert_before(self, name):
        context = api.llvm.getGlobalContext()
        ptr = api.llvm.BasicBlock.Create(context, name, self.function._ptr,
                                    self._ptr)
        return _make_value(ptr)

    def delete(self):
        _ValueFactory.delete(self._ptr)
        self._ptr.eraseFromParent()

    @property
    def function(self):
        return _make_value(self._ptr.getParent())

    @property
    def instructions(self):
        return list(map(_make_value, self._ptr.getInstList()))

#===----------------------------------------------------------------------===
# Value factory method
#===----------------------------------------------------------------------===


class _ValueFactory(object):
    cache = weakref.WeakValueDictionary()

    # value ID -> class map
    class_for_valueid = {
        VALUE_ARGUMENT                        : Argument,
        VALUE_BASIC_BLOCK                     : BasicBlock,
        VALUE_FUNCTION                        : Function,
        VALUE_GLOBAL_ALIAS                    : GlobalValue,
        VALUE_GLOBAL_VARIABLE                 : GlobalVariable,
        VALUE_UNDEF_VALUE                     : UndefValue,
        VALUE_CONSTANT_EXPR                   : ConstantExpr,
        VALUE_CONSTANT_AGGREGATE_ZERO         : ConstantAggregateZero,
        VALUE_CONSTANT_DATA_ARRAY             : ConstantDataArray,
        VALUE_CONSTANT_DATA_VECTOR            : ConstantDataVector,
        VALUE_CONSTANT_INT                    : ConstantInt,
        VALUE_CONSTANT_FP                     : ConstantFP,
        VALUE_CONSTANT_ARRAY                  : ConstantArray,
        VALUE_CONSTANT_STRUCT                 : ConstantStruct,
        VALUE_CONSTANT_VECTOR                 : ConstantVector,
        VALUE_CONSTANT_POINTER_NULL           : ConstantPointerNull,
        VALUE_MD_NODE                         : MetaData,
        VALUE_MD_STRING                       : MetaDataString,
        VALUE_INLINE_ASM                      : InlineAsm,
        VALUE_INSTRUCTION + OPCODE_PHI        : PHINode,
        VALUE_INSTRUCTION + OPCODE_CALL       : CallOrInvokeInstruction,
        VALUE_INSTRUCTION + OPCODE_INVOKE     : CallOrInvokeInstruction,
        VALUE_INSTRUCTION + OPCODE_SWITCH     : SwitchInstruction,
        VALUE_INSTRUCTION + OPCODE_ICMP       : CompareInstruction,
        VALUE_INSTRUCTION + OPCODE_FCMP       : CompareInstruction
    }

    @classmethod
    def build(cls, ptr):
        # try to look in the cache
        addr = ptr._capsule.pointer
        id = ptr.getValueID()
        key = id, addr
        try:
            obj = cls.cache[key]
            return obj
        except KeyError:
            pass
        # find class by value id
        ctorcls = cls.class_for_valueid.get(id)
        if not ctorcls:
            if id > VALUE_INSTRUCTION: # "generic" instruction
                ctorcls = Instruction
            else: # "generic" value
                ctorcls = Value
        # cache the obj
        obj = ctorcls(_ValueFactory, ptr)
        cls.cache[key] = obj
        return obj

    @classmethod
    def delete(cls, ptr):
        del cls.cache[(ptr.getValueID(), ptr._capsule.pointer)]

def _make_value(ptr):
    return _ValueFactory.build(ptr)

#===----------------------------------------------------------------------===
# Builder
#===----------------------------------------------------------------------===

_atomic_orderings = {
    'unordered' : api.llvm.AtomicOrdering.Unordered,
    'monotonic' : api.llvm.AtomicOrdering.Monotonic,
    'acquire'   : api.llvm.AtomicOrdering.Acquire,
    'release'   : api.llvm.AtomicOrdering.Release,
    'acq_rel'   : api.llvm.AtomicOrdering.AcquireRelease,
    'seq_cst'   : api.llvm.AtomicOrdering.SequentiallyConsistent
}

class Builder(llvm.Wrapper):

    @staticmethod
    def new(basic_block):
        context = api.llvm.getGlobalContext()
        ptr = api.llvm.IRBuilder.new(context)
        ptr.SetInsertPoint(basic_block._ptr)
        return Builder(ptr)

    def position_at_beginning(self, bblk):
        """Position the builder at the beginning of the given block.

        Next instruction inserted will be first one in the block."""

        # Instruction list won't be long anyway,
        # Does not matter much to build a list of all instructions
        instrs = bblk.instructions
        if instrs:
            self.position_before(instrs[0])
        else:
            self.position_at_end(bblk)

    def position_at_end(self, bblk):
        """Position the builder at the end of the given block.

        Next instruction inserted will be last one in the block."""

        self._ptr.SetInsertPoint(bblk._ptr)

    def position_before(self, instr):
        """Position the builder before the given instruction.

            The instruction can belong to a basic block other than the
            current one."""
        self._ptr.SetInsertPoint(instr._ptr)

    @property
    def basic_block(self):
        """The basic block where the builder is positioned."""
        return _make_value(self._ptr.GetInsertBlock())

    # terminator instructions
    def _guard_terminators(self):
        if __debug__:
            import warnings
            for instr in self.basic_block.instructions:
                if instr.is_terminator:
                    warnings.warn("BasicBlock can only have one terminator")

    def ret_void(self):
        self._guard_terminators()
        return _make_value(self._ptr.CreateRetVoid())

    def ret(self, value):
        self._guard_terminators()
        return _make_value(self._ptr.CreateRet(value._ptr))

    def ret_many(self, values):
        self._guard_terminators()
        values = llvm._extract_ptrs(values)
        return _make_value(self._ptr.CreateAggregateRet(values, len(values)))

    def branch(self, bblk):
        self._guard_terminators()
        return _make_value(self._ptr.CreateBr(bblk._ptr))

    def cbranch(self, if_value, then_blk, else_blk):
        self._guard_terminators()
        return _make_value(self._ptr.CreateCondBr(if_value._ptr,
                                            then_blk._ptr,
                                            else_blk._ptr))

    def switch(self, value, else_blk, n=10):
        self._guard_terminators()
        return _make_value(self._ptr.CreateSwitch(value._ptr,
                                                  else_blk._ptr,
                                                  n))

    def invoke(self, func, args, then_blk, catch_blk, name=""):
        self._guard_terminators()
        return _make_value(self._ptr.CreateInvoke(func._ptr,
                                                  then_blk._ptr,
                                                  catch_blk._ptr,
                                                  llvm._extract_ptrs(args)))

    def unreachable(self):
        self._guard_terminators()
        return _make_value(self._ptr.CreateUnreachable())

    # arithmethic, bitwise and logical

    def add(self, lhs, rhs, name="", nuw=False, nsw=False):
        return _make_value(self._ptr.CreateAdd(lhs._ptr, rhs._ptr, name,
                                               nuw, nsw))

    def fadd(self, lhs, rhs, name=""):
        return _make_value(self._ptr.CreateFAdd(lhs._ptr, rhs._ptr, name))

    def sub(self, lhs, rhs, name="", nuw=False, nsw=False):
        return _make_value(self._ptr.CreateSub(lhs._ptr, rhs._ptr, name,
                                               nuw, nsw))

    def fsub(self, lhs, rhs, name=""):
        return _make_value(self._ptr.CreateFSub(lhs._ptr, rhs._ptr, name))

    def mul(self, lhs, rhs, name="", nuw=False, nsw=False):
        return _make_value(self._ptr.CreateMul(lhs._ptr, rhs._ptr, name,
                                               nuw, nsw))

    def fmul(self, lhs, rhs, name=""):
        return _make_value(self._ptr.CreateFMul(lhs._ptr, rhs._ptr, name))

    def udiv(self, lhs, rhs, name="", exact=False):
        return _make_value(self._ptr.CreateUDiv(lhs._ptr, rhs._ptr, name,
                                                exact))

    def sdiv(self, lhs, rhs, name="", exact=False):
        return _make_value(self._ptr.CreateSDiv(lhs._ptr, rhs._ptr, name,
                                                exact))

    def fdiv(self, lhs, rhs, name=""):
        return _make_value(self._ptr.CreateFDiv(lhs._ptr, rhs._ptr, name))

    def urem(self, lhs, rhs, name=""):
        return _make_value(self._ptr.CreateURem(lhs._ptr, rhs._ptr, name))

    def srem(self, lhs, rhs, name=""):
        return _make_value(self._ptr.CreateSRem(lhs._ptr, rhs._ptr, name))

    def frem(self, lhs, rhs, name=""):
        return _make_value(self._ptr.CreateFRem(lhs._ptr, rhs._ptr, name))

    def shl(self, lhs, rhs, name="", nuw=False, nsw=False):
        return _make_value(self._ptr.CreateShl(lhs._ptr, rhs._ptr, name,
                                               nuw, nsw))

    def lshr(self, lhs, rhs, name="", exact=False):
        return _make_value(self._ptr.CreateLShr(lhs._ptr, rhs._ptr, name,
                                                exact))

    def ashr(self, lhs, rhs, name="", exact=False):
        return _make_value(self._ptr.CreateAShr(lhs._ptr, rhs._ptr, name,
                                                exact))

    def and_(self, lhs, rhs, name=""):
        return _make_value(self._ptr.CreateAnd(lhs._ptr, rhs._ptr, name))

    def or_(self, lhs, rhs, name=""):
        return _make_value(self._ptr.CreateOr(lhs._ptr, rhs._ptr, name))

    def xor(self, lhs, rhs, name=""):
        return _make_value(self._ptr.CreateXor(lhs._ptr, rhs._ptr, name))

    def neg(self, val, name="", nuw=False, nsw=False):
        return _make_value(self._ptr.CreateNeg(val._ptr, name, nuw, nsw))

    def not_(self, val, name=""):
        return _make_value(self._ptr.CreateNot(val._ptr, name))

    # memory

    def malloc(self, ty, name=""):
        context = api.llvm.getGlobalContext()
        allocsz = api.llvm.ConstantExpr.getSizeOf(ty._ptr)
        ity = allocsz.getType()
        malloc = api.llvm.CallInst.CreateMalloc(self.basic_block._ptr,
                                                ity,
                                                ty._ptr,
                                                allocsz,
                                                None,
                                                None,
                                                "")
        inst = self._ptr.Insert(malloc, name)
        return _make_value(inst)

    def malloc_array(self, ty, size, name=""):
        context = api.llvm.getGlobalContext()
        allocsz = api.llvm.ConstantExpr.getSizeOf(ty._ptr)
        ity = allocsz.getType()
        malloc = api.llvm.CallInst.CreateMalloc(self.basic_block._ptr,
                                                ity,
                                                ty._ptr,
                                                allocsz,
                                                size._ptr,
                                                None,
                                                "")
        inst = self._ptr.Insert(malloc, name)
        return _make_value(inst)

    def alloca(self, ty, name=""):
        intty = Type.int()
        return _make_value(self._ptr.CreateAlloca(ty._ptr, None, name))

    def alloca_array(self, ty, size, name=""):
        return _make_value(self._ptr.CreateAlloca(ty._ptr, size._ptr, name))

    def free(self, ptr):
        free = api.llvm.CallInst.CreateFree(ptr._ptr, self.basic_block._ptr)
        inst = self._ptr.Insert(free)
        return _make_value(inst)

    def load(self, ptr, name="", align=0, volatile=False, invariant=False):
        inst = _make_value(self._ptr.CreateLoad(ptr._ptr, name))
        if align:
            inst._ptr.setAlignment(align)
        if volatile:
            inst.set_volatile(volatile)
        if invariant:
            mod = self.basic_block.function.module
            md = MetaData.get(mod, []) # empty metadata node
            inst.set_metadata('invariant.load', md)
        return inst

    def store(self, value, ptr, align=0, volatile=False):
        inst = _make_value(self._ptr.CreateStore(value._ptr, ptr._ptr))
        if align:
            inst._ptr.setAlignment(align)
        if volatile:
            inst.set_volatile(volatile)
        return inst

    def gep(self, ptr, indices, name="", inbounds=False):
        if inbounds:
            ret = self._ptr.CreateInBoundsGEP(ptr._ptr,
                                              llvm._extract_ptrs(indices),
                                              name)
        else:
            ret = self._ptr.CreateGEP(ptr._ptr,
                                      llvm._extract_ptrs(indices),
                                      name)
        return _make_value(ret)

    # casts and extensions

    def trunc(self, value, dest_ty, name=""):
        return _make_value(self._ptr.CreateTrunc(value._ptr, dest_ty._ptr, name))

    def zext(self, value, dest_ty, name=""):
        return _make_value(self._ptr.CreateZExt(value._ptr, dest_ty._ptr, name))

    def sext(self, value, dest_ty, name=""):
        return _make_value(self._ptr.CreateSExt(value._ptr, dest_ty._ptr, name))

    def fptoui(self, value, dest_ty, name=""):
        return _make_value(self._ptr.CreateFPToUI(value._ptr, dest_ty._ptr, name))

    def fptosi(self, value, dest_ty, name=""):
        return _make_value(self._ptr.CreateFPToSI(value._ptr, dest_ty._ptr, name))

    def uitofp(self, value, dest_ty, name=""):
        return _make_value(self._ptr.CreateUIToFP(value._ptr, dest_ty._ptr, name))

    def sitofp(self, value, dest_ty, name=""):
        return _make_value(self._ptr.CreateSIToFP(value._ptr, dest_ty._ptr, name))

    def fptrunc(self, value, dest_ty, name=""):
        return _make_value(self._ptr.CreateFPTrunc(value._ptr, dest_ty._ptr, name))

    def fpext(self, value, dest_ty, name=""):
        return _make_value(self._ptr.CreateFPExt(value._ptr, dest_ty._ptr, name))

    def ptrtoint(self, value, dest_ty, name=""):
        return _make_value(self._ptr.CreatePtrToInt(value._ptr, dest_ty._ptr, name))

    def inttoptr(self, value, dest_ty, name=""):
        return _make_value(self._ptr.CreateIntToPtr(value._ptr, dest_ty._ptr, name))

    def bitcast(self, value, dest_ty, name=""):
        return _make_value(self._ptr.CreateBitCast(value._ptr, dest_ty._ptr, name))

    # comparisons

    def icmp(self, ipred, lhs, rhs, name=""):
        return _make_value(self._ptr.CreateICmp(ipred, lhs._ptr, rhs._ptr, name))

    def fcmp(self, rpred, lhs, rhs, name=""):
        return _make_value(self._ptr.CreateFCmp(rpred, lhs._ptr, rhs._ptr, name))

    # misc

    def extract_value(self, retval, idx, name=""):
        return _make_value(self._ptr.CreateExtractValue(retval._ptr, [idx], name))

    # obsolete synonym for extract_value
    getresult = extract_value

    def insert_value(self, retval, rhs, idx, name=""):
        return _make_value(self._ptr.CreateInsertValue(retval._ptr,
                                                       rhs._ptr,
                                                       [idx],
                                                       name))

    def phi(self, ty, name=""):
        return _make_value(self._ptr.CreatePHI(ty._ptr, 2, name))

    def call(self, fn, args, name=""):
        err_template = 'Argument type mismatch: expected %s but got %s'

        for i, (t, v) in enumerate(zip(fn.type.pointee.args, args)):
            if  t != v.type:
                raise TypeError(err_template % (t, v.type))
        arg_ptrs = llvm._extract_ptrs(args)
        return _make_value(self._ptr.CreateCall(fn._ptr, arg_ptrs, name))

    def select(self, cond, then_value, else_value, name=""):
        return _make_value(self._ptr.CreateSelect(cond._ptr, then_value._ptr,
                                            else_value._ptr, name))

    def vaarg(self, list_val, ty, name=""):
        return _make_value(self._ptr.CreateVAArg(list_val._ptr, ty._ptr, name))

    def extract_element(self, vec_val, idx_val, name=""):
        return _make_value(self._ptr.CreateExtractElement(vec_val._ptr,
                                                          idx_val._ptr,
                                                          name))


    def insert_element(self, vec_val, elt_val, idx_val, name=""):
        return _make_value(self._ptr.CreateInsertElement(vec_val._ptr,
                                                          elt_val._ptr,
                                                          idx_val._ptr,
                                                          name))

    def shuffle_vector(self, vecA, vecB, mask, name=""):
        return _make_value(self._ptr.CreateShuffleVector(vecA._ptr,
                                                         vecB._ptr,
                                                         mask._ptr,
                                                         name))
    # atomics

    def atomic_cmpxchg(self, ptr, old, new, ordering, crossthread=True):
        return _make_value(self._ptr.CreateAtomicCmpXchg(ptr._ptr,
                                                   old._ptr,
                                                   new._ptr,
                                                   _atomic_orderings[ordering],
                                                   _sync_scope(crossthread)))

    def atomic_rmw(self, op, ptr, val, ordering, crossthread=True):
        op_dict = dict((k.lower(), v)
                       for k, v in vars(api.llvm.AtomicRMWInst.BinOp).items())
        op = op_dict[op]
        return _make_value(self._ptr.CreateAtomicRMW(op, ptr._ptr, val._ptr,
                                               _atomic_orderings[ordering],
                                               _sync_scope(crossthread)))

    def atomic_xchg(self, *args, **kwargs):
        return self.atomic_rmw('xchg', *args, **kwargs)

    def atomic_add(self, *args, **kwargs):
        return self.atomic_rmw('add', *args, **kwargs)

    def atomic_sub(self, *args, **kwargs):
        return self.atomic_rmw('sub', *args, **kwargs)

    def atomic_and(self, *args, **kwargs):
        return self.atomic_rmw('and', *args, **kwargs)

    def atomic_nand(self, *args, **kwargs):
        return self.atomic_rmw('nand', *args, **kwargs)

    def atomic_or(self, *args, **kwargs):
        return self.atomic_rmw('or', *args, **kwargs)

    def atomic_xor(self, *args, **kwargs):
        return self.atomic_rmw('xor', *args, **kwargs)

    def atomic_max(self, *args, **kwargs):
        return self.atomic_rmw('max', *args, **kwargs)

    def atomic_min(self, *args, **kwargs):
        return self.atomic_rmw('min', *args, **kwargs)

    def atomic_umax(self, *args, **kwargs):
        return self.atomic_rmw('umax', *args, **kwargs)

    def atomic_umin(self, *args, **kwargs):
        return self.atomic_rmw('umin', *args, **kwargs)

    def atomic_load(self, ptr, ordering, align=1, crossthread=True,
                    volatile=False, name=""):
        inst = self.load(ptr, align=align, volatile=volatile, name=name)
        inst._ptr.setAtomic(_atomic_orderings[ordering],
                            _sync_scope(crossthread))
        return inst

    def atomic_store(self, value, ptr, ordering, align=1, crossthread=True,
                     volatile=False):
        inst = self.store(value, ptr, align=align, volatile=volatile)
        inst._ptr.setAtomic(_atomic_orderings[ordering],
                            _sync_scope(crossthread))
        return inst


    def fence(self, ordering, crossthread=True):
        return _make_value(self._ptr.CreateFence(_atomic_orderings[ordering],
                                                 _sync_scope(crossthread)))

def _sync_scope(crossthread):
    if crossthread:
        scope = api.llvm.SynchronizationScope.CrossThread
    else:
        scope = api.llvm.SynchronizationScope.SingleThread
    return scope

def load_library_permanently(filename):
    """Load a shared library.

    Load the given shared library (filename argument specifies the full
    path of the .so file) using LLVM. Symbols from these are available
    from the execution engine thereafter."""
    with contextlib.closing(BytesIO()) as errmsg:
        failed = api.llvm.sys.DynamicLibrary.LoadPermanentLibrary(filename,
                                                                  errmsg)
        if failed:
            raise llvm.LLVMException(errmsg.getvalue())

def inline_function(call):
    info = api.llvm.InlineFunctionInfo.new()
    return api.llvm.InlineFunction(call._ptr, info)

def parse_environment_options(progname, envname):
    api.llvm.cl.ParseEnvironmentOptions(progname, envname)

if api.llvm.InitializeNativeTarget():
    raise llvm.LLVMException("No native target!?")
if api.llvm.InitializeNativeTargetAsmPrinter():
    # should this be an optional feature?
    # should user trigger the initialization?
    raise llvm.LLVMException("No native asm printer!?")
if api.llvm.InitializeNativeTargetAsmParser():
    # required by MCJIT?
    # should this be an optional feature?
    # should user trigger the initialization?
    raise llvm.LLVMException("No native asm parser!?")
