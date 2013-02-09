try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import contextlib

import llvm

import api

#===----------------------------------------------------------------------===
# Enumerations
#===----------------------------------------------------------------------===

# type id (llvm::Type::TypeID)
TYPE_VOID       = api.llvm.Type.TypeID.VoidTyID
TYPE_HALF       = api.llvm.Type.TypeID.HalfTyID
TYPE_FLOAT      = api.llvm.Type.TypeID.FloatTyID
TYPE_DOUBLE     = api.llvm.Type.TypeID.DoubleTyID
TYPE_X86_FP80   = api.llvm.Type.TypeID.X86_FP80TyID
TYPE_FP128      = api.llvm.Type.TypeID.FP128TyID
TYPE_PPC_FP128  = api.llvm.Type.TypeID.PPC_FP128TyID
TYPE_LABEL      = api.llvm.Type.TypeID.LabelTyID
TYPE_INTEGER    = api.llvm.Type.TypeID.IntegerTyID
TYPE_FUNCTION   = api.llvm.Type.TypeID.FunctionTyID
TYPE_STRUCT     = api.llvm.Type.TypeID.StructTyID
TYPE_ARRAY      = api.llvm.Type.TypeID.ArrayTyID
TYPE_POINTER    = api.llvm.Type.TypeID.PointerTyID
TYPE_VECTOR     = api.llvm.Type.TypeID.VectorTyID
TYPE_METADATA   = api.llvm.Type.TypeID.MetadataTyID
TYPE_X86_MMX    = api.llvm.Type.TypeID.X86_MMXTyID


# value IDs (llvm::Value::ValueTy enum)
# According to the doxygen docs, it is not a good idea to use these enums.
# There are more values than those declared.
VALUE_ARGUMENT                          = api.llvm.Value.ValueTy.ArgumentVal
VALUE_BASIC_BLOCK                       = api.llvm.Value.ValueTy.BasicBlockVal
VALUE_FUNCTION                          = api.llvm.Value.ValueTy.FunctionVal
VALUE_GLOBAL_ALIAS                      = api.llvm.Value.ValueTy.GlobalAliasVal
VALUE_GLOBAL_VARIABLE                   = api.llvm.Value.ValueTy.GlobalVariableVal
VALUE_UNDEF_VALUE                       = api.llvm.Value.ValueTy.UndefValueVal
VALUE_BLOCK_ADDRESS                     = api.llvm.Value.ValueTy.BlockAddressVal
VALUE_CONSTANT_EXPR                     = api.llvm.Value.ValueTy.ConstantExprVal
VALUE_CONSTANT_AGGREGATE_ZERO           = api.llvm.Value.ValueTy.ConstantAggregateZeroVal
VALUE_CONSTANT_DATA_ARRAY               = api.llvm.Value.ValueTy.ConstantDataArrayVal
VALUE_CONSTANT_DATA_VECTOR              = api.llvm.Value.ValueTy.ConstantDataVectorVal
VALUE_CONSTANT_INT                      = api.llvm.Value.ValueTy.ConstantIntVal
VALUE_CONSTANT_FP                       = api.llvm.Value.ValueTy.ConstantFPVal
VALUE_CONSTANT_ARRAY                    = api.llvm.Value.ValueTy.ConstantArrayVal
VALUE_CONSTANT_STRUCT                   = api.llvm.Value.ValueTy.ConstantStructVal
VALUE_CONSTANT_VECTOR                   = api.llvm.Value.ValueTy.ConstantVectorVal
VALUE_CONSTANT_POINTER_NULL             = api.llvm.Value.ValueTy.ConstantPointerNullVal
VALUE_MD_NODE                           = api.llvm.Value.ValueTy.MDNodeVal
VALUE_MD_STRING                         = api.llvm.Value.ValueTy.MDStringVal
VALUE_INLINE_ASM                        = api.llvm.Value.ValueTy.InlineAsmVal
VALUE_PSEUDO_SOURCE_VALUE               = api.llvm.Value.ValueTy.PseudoSourceValueVal
VALUE_FIXED_STACK_PSEUDO_SOURCE_VALUE   = api.llvm.Value.ValueTy.FixedStackPseudoSourceValueVal
VALUE_INSTRUCTION                       = api.llvm.Value.ValueTy.InstructionVal

## instruction opcodes (from include/llvm/Instruction.def)
#OPCODE_RET            = 1
#OPCODE_BR             = 2
#OPCODE_SWITCH         = 3
#OPCODE_INDIRECT_BR    = 4
#OPCODE_INVOKE         = 5
#OPCODE_RESUME         = 6
#OPCODE_UNREACHABLE    = 7
#OPCODE_ADD            = 8
#OPCODE_FADD           = 9
#OPCODE_SUB            = 10
#OPCODE_FSUB           = 11
#OPCODE_MUL            = 12
#OPCODE_FMUL           = 13
#OPCODE_UDIV           = 14
#OPCODE_SDIV           = 15
#OPCODE_FDIV           = 16
#OPCODE_UREM           = 17
#OPCODE_SREM           = 18
#OPCODE_FREM           = 19
#OPCODE_SHL            = 20
#OPCODE_LSHR           = 21
#OPCODE_ASHR           = 22
#OPCODE_AND            = 23
#OPCODE_OR             = 24
#OPCODE_XOR            = 25
#OPCODE_ALLOCA         = 26
#OPCODE_LOAD           = 27
#OPCODE_STORE          = 28
#OPCODE_GETELEMENTPTR  = 29
#OPCODE_FENCE          = 30
#OPCODE_ATOMICCMPXCHG  = 31
#OPCODE_ATOMICRMW      = 32
#OPCODE_TRUNC          = 33
#OPCODE_ZEXT           = 34
#OPCODE_SEXT           = 35
#OPCODE_FPTOUI         = 36
#OPCODE_FPTOSI         = 37
#OPCODE_UITOFP         = 38
#OPCODE_SITOFP         = 39
#OPCODE_FPTRUNC        = 40
#OPCODE_FPEXT          = 41
#OPCODE_PTRTOINT       = 42
#OPCODE_INTTOPTR       = 43
#OPCODE_BITCAST        = 44
#OPCODE_ICMP           = 45
#OPCODE_FCMP           = 46
#OPCODE_PHI            = 47
#OPCODE_CALL           = 48
#OPCODE_SELECT         = 49
#OPCODE_USEROP1        = 50
#OPCODE_USEROP2        = 51
#OPCODE_VAARG          = 52
#OPCODE_EXTRACTELEMENT = 53
#OPCODE_INSERTELEMENT  = 54
#OPCODE_SHUFFLEVECTOR  = 55
#OPCODE_EXTRACTVALUE   = 56
#OPCODE_INSERTVALUE    = 57
#OPCODE_LANDINGPAD     = 58
#
## calling conventions
#CC_C             = 0
#CC_FASTCALL      = 8
#CC_COLDCALL      = 9
#CC_GHC           = 10
#CC_X86_STDCALL   = 64
#CC_X86_FASTCALL  = 65
#CC_ARM_APCS      = 66
#CC_ARM_AAPCS     = 67
#CC_ARM_AAPCS_VFP = 68
#CC_MSP430_INTR   = 69
#CC_X86_THISCALL  = 70
#CC_PTX_KERNEL    = 71
#CC_PTX_DEVICE    = 72
#CC_MBLAZE_INTR   = 73
#CC_MBLAZE_SVOL   = 74
#
#
## int predicates
#ICMP_EQ         = 32
#ICMP_NE         = 33
#ICMP_UGT        = 34
#ICMP_UGE        = 35
#ICMP_ULT        = 36
#ICMP_ULE        = 37
#ICMP_SGT        = 38
#ICMP_SGE        = 39
#ICMP_SLT        = 40
#ICMP_SLE        = 41
#
## same as ICMP_xx, for backward compatibility
#IPRED_EQ        = ICMP_EQ
#IPRED_NE        = ICMP_NE
#IPRED_UGT       = ICMP_UGT
#IPRED_UGE       = ICMP_UGE
#IPRED_ULT       = ICMP_ULT
#IPRED_ULE       = ICMP_ULE
#IPRED_SGT       = ICMP_SGT
#IPRED_SGE       = ICMP_SGE
#IPRED_SLT       = ICMP_SLT
#IPRED_SLE       = ICMP_SLE
#
## real predicates
#FCMP_FALSE      = 0
#FCMP_OEQ        = 1
#FCMP_OGT        = 2
#FCMP_OGE        = 3
#FCMP_OLT        = 4
#FCMP_OLE        = 5
#FCMP_ONE        = 6
#FCMP_ORD        = 7
#FCMP_UNO        = 8
#FCMP_UEQ        = 9
#FCMP_UGT        = 10
#FCMP_UGE        = 11
#FCMP_ULT        = 12
#FCMP_ULE        = 13
#FCMP_UNE        = 14
#FCMP_TRUE       = 15
#
## real predicates
#RPRED_FALSE     = FCMP_FALSE
#RPRED_OEQ       = FCMP_OEQ
#RPRED_OGT       = FCMP_OGT
#RPRED_OGE       = FCMP_OGE
#RPRED_OLT       = FCMP_OLT
#RPRED_OLE       = FCMP_OLE
#RPRED_ONE       = FCMP_ONE
#RPRED_ORD       = FCMP_ORD
#RPRED_UNO       = FCMP_UNO
#RPRED_UEQ       = FCMP_UEQ
#RPRED_UGT       = FCMP_UGT
#RPRED_UGE       = FCMP_UGE
#RPRED_ULT       = FCMP_ULT
#RPRED_ULE       = FCMP_ULE
#RPRED_UNE       = FCMP_UNE
#RPRED_TRUE      = FCMP_TRUE
#
## linkages (see llvm-c/Core.h)
#LINKAGE_EXTERNAL                        = 0
#LINKAGE_AVAILABLE_EXTERNALLY            = 1
#LINKAGE_LINKONCE_ANY                    = 2
#LINKAGE_LINKONCE_ODR                    = 3
#LINKAGE_WEAK_ANY                        = 4
#LINKAGE_WEAK_ODR                        = 5
#LINKAGE_APPENDING                       = 6
#LINKAGE_INTERNAL                        = 7
#LINKAGE_PRIVATE                         = 8
#LINKAGE_DLLIMPORT                       = 9
#LINKAGE_DLLEXPORT                       = 10
#LINKAGE_EXTERNAL_WEAK                   = 11
#LINKAGE_GHOST                           = 12
#LINKAGE_COMMON                          = 13
#LINKAGE_LINKER_PRIVATE                  = 14
#LINKAGE_LINKER_PRIVATE_WEAK             = 15
#LINKAGE_LINKER_PRIVATE_WEAK_DEF_AUTO    = 16
#
## visibility (see llvm/GlobalValue.h)
#VISIBILITY_DEFAULT   = 0
#VISIBILITY_HIDDEN    = 1
#VISIBILITY_PROTECTED = 2

# parameter attributes llvm::Attributes::AttrVal (see llvm/Attributes.h)
ATTR_NONE               = api.llvm.Attributes.AttrVal.None_
ATTR_ZEXT               = api.llvm.Attributes.AttrVal.ZExt
ATTR_SEXT               = api.llvm.Attributes.AttrVal.SExt
ATTR_NO_RETURN          = api.llvm.Attributes.AttrVal.NoReturn
ATTR_IN_REG             = api.llvm.Attributes.AttrVal.InReg
ATTR_STRUCT_RET         = api.llvm.Attributes.AttrVal.StructRet
ATTR_NO_UNWIND          = api.llvm.Attributes.AttrVal.NoUnwind
ATTR_NO_ALIAS           = api.llvm.Attributes.AttrVal.NoAlias
ATTR_BY_VAL             = api.llvm.Attributes.AttrVal.ByVal
ATTR_NEST               = api.llvm.Attributes.AttrVal.Nest
ATTR_READ_NONE          = api.llvm.Attributes.AttrVal.ReadNone
ATTR_READONLY           = api.llvm.Attributes.AttrVal.ReadOnly
ATTR_NO_INLINE          = api.llvm.Attributes.AttrVal.NoInline
ATTR_ALWAYS_INLINE      = api.llvm.Attributes.AttrVal.AlwaysInline
ATTR_OPTIMIZE_FOR_SIZE  = api.llvm.Attributes.AttrVal.OptimizeForSize
ATTR_STACK_PROTECT      = api.llvm.Attributes.AttrVal.StackProtect
ATTR_STACK_PROTECT_REQ  = api.llvm.Attributes.AttrVal.StackProtectReq
ATTR_ALIGNMENT          = api.llvm.Attributes.AttrVal.Alignment
ATTR_NO_CAPTURE         = api.llvm.Attributes.AttrVal.NoCapture
ATTR_NO_REDZONE         = api.llvm.Attributes.AttrVal.NoRedZone
ATTR_NO_IMPLICIT_FLOAT  = api.llvm.Attributes.AttrVal.NoImplicitFloat
ATTR_NAKED              = api.llvm.Attributes.AttrVal.Naked
ATTR_INLINE_HINT        = api.llvm.Attributes.AttrVal.InlineHint
ATTR_STACK_ALIGNMENT    = api.llvm.Attributes.AttrVal.StackAlignment


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
        errbuf = StringIO()
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
        errbuf = StringIO()
        m = api.llvm.ParseAssemblyString(ir, None, api.llvm.SMDIagnostic.new(), context)
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
        return self.getPointerSize()

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
        enum_mode = api.llvm.Linker.LinkMode
        mode = enum_mode.PreserveSource if preserve else enum_mode.DestroySource

        with contextlib.closing(StringIO()) as errmsg:
            failed = api.llvm.Linker.LinkModule(self._ptr,
                                           other._ptr,
                                           mode,
                                           errmsg)
            if failed:
                raise llvm.LLVMException(errmsg)

    def get_type_named(self, name):
        typ = self._ptr.getTypeByName(name)
        return StructType(typ)

    def add_global_variable(self, ty, name, addrspace=0):
        """Add a global variable of given type with given name."""
        external = api.llvm.GlobalVariable.LinkageTypes.ExternalLinkage
        notthreadlocal = api.llvm.GlobalVariable.ThreadLocalMode.NotThreadLocal
        init = None
        insertbefore = None
        ptr = api.llvm.GlobalVariable.new(self,
                                     ty._ptr,
                                     False,
                                     external,
                                     init,
                                     name,
                                     insertbefore,
                                     notthreadlocal,
                                     addrspace)
        return GlobalVariable(ptr)

    def get_global_variable_named(self, name):
        """Return a GlobalVariable object for the given name."""
        ptr = self._ptr.getNamedGlobal(name)
        return GlobalVariable(ptr)

    @property
    def global_variables(self):
        return self._ptr.list_globals()

    def add_function(self, ty, name):
        """Add a function of given type with given name."""
        fn = self.get_function_named(name)
        if fn is not None:
            raise llvm.LLVMException("Duplicated function %s" % name)
        return self.get_or_insert_function(ty, name)

    def get_function_named(self, name):
        """Return a Function object representing function with given name."""
        fn = self._ptr.getFunction(name)
        if fn is None:
            return None
        return Function(fn)

    def get_or_insert_function(self, ty, name):
        """Like get_function_named(), but does add_function() first, if
           function is not present."""
        constant = self._ptr.getOrInsertFunction(name, ty._ptr)
        fn = constant._downcast(api.llvm.Function)
        return Function(fn)

    @property
    def functions(self):
        """All functions in this module."""
        return map(Function, self._ptr.list_functions())

    def verify(self):
        """Verify module.

            Checks module for errors. Raises `llvm.LLVMException' on any
            error."""
        action = api.llvm.VerifierFailureAction.ReturnStatusAction
        errio = StringIO()
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
            fileobj = StringIO
        api.llvm.WriteBitcodeToFile(self._ptr, fileobj)
        if ret:
            return fileobj.getvalue()

    def _get_id(self):
        return self._ptr.getModuleIdentifier(self._ptr)

    def _set_id(self, string):
        self._ptr.setModuleIdentifier(string)

    id = property(_get_id, _set_id)

    def _to_native_something(self, fileobj, cgft):
        ret = False
        if fileobj is None:
            ret = True
            fileobj = StringIO()
        cgft = api.llvm.TargetMachine.CodeGenFileType.CGFT_AssemblyFile
        cgft = api.llvm.TargetMachine.CodeGenFileType.CGFT_ObjectFile
        failed = tm.addPassesToEmitFile(pm, formatted, cgft, False)
        if failed:
            raise llvm.LLVMException("Failed to write native object file")
        if ret:
            return fileobj.getvalue()


    def to_native_object(self, fileobj=None):
        '''Outputs the byte string of the module as native object code

        If a fileobj is given, the output is written to it;
        Otherwise, the output is returned
        '''
        CGFT = api.llvm.TargetMachine.CodeGenFileType
        return self._to_native_something(fileobj, CGFT.CGFT_ObjectFile)

    def to_native_assembly(self, fileobj=None):
        '''Outputs the byte string of the module as native assembly code

        If a fileobj is given, the output is written to it;
        Otherwise, the output is returned
        '''
        CGFT = api.llvm.TargetMachine.CodeGenFileType
        return self._to_native_something(fileobj, CGFT.CGFT_AssemblyFile)

    def get_or_insert_named_metadata(self, name):
        return NamedMetadata(self._ptr.getOrInsertNamedMetadata(name))

    def get_named_metadata(self, name):
        return NamedMetadata(self._ptr.get_named_metadata(name))

    def clone(self):
        return NamedMetadata(api.llvm.CloneModule(self._ptr))

class Type(llvm.Wrapper):
    """Represents a type, like a 32-bit integer or an 80-bit x86 float.

    Use one of the static methods to create an instance. Example:
    ty = Type.double()
    """

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
        ptr = api.llvm.StructType.create(context)
        ptr.setBody(_extract_ptrs(element_tys), is_packed)
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
        ptr = api.llvm.StructType.create(context)
        ptr.setBody(_extract_ptrs(element_tys), is_packed)
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

    def __eq__(self, rhs):
        return self._ptr is rhs._ptr

    def __ne__(self, rhs):
        return not (self == rhs)

class IntegerType(Type):
    """Represents an integer type."""

    @property
    def width(self):
        """The width of the integer type, in bits."""
        return self._ptr.getIntegerBitWidth()

class FunctionType(Type):
    """Represents a function type."""

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
        tys = [Type(self._ptr.getParamType(i)) for i in range(self.arg_count)]

    @property
    def arg_count(self):
        """Number of arguments accepted by this function.

            Same as len(obj.args), but faster."""
        return self._ptr.getNumParams()



class StructType(Type):
    """Represents a structure type."""

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
        return self._ptr.getName()

    name = property(_get_name, _set_name)

    @property
    def is_literal(self):
        return self.isLiteral()

    @property
    def is_identified(self):
        return not self.is_literal()

    @property
    def is_opaque(self):
        return self.isOpaque()

class ArrayType(Type):
    """Represents an array type."""

    @property
    def element(self):
        return Type(self._ptr.getArrayElementType())

    @property
    def count(self):
        return self._ptr.getNumElements()

class PointerType(Type):

    @property
    def pointee(self):
        return Type(self._ptr.getPointerElementType())

    @property
    def address_space(self):
        return self._ptr.getAddressSpace()

class VectorType(Type):

    @property
    def element(self):
        return self._ptr.getVectorElementType()

    @property
    def count(self):
        return self._ptr.getNumElements()

class Value(llvm.Wrapper):

    def __str__(self):
        return str(self._ptr)

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
        return map(User, self._ptr.list_use())

class User(Value):

    @property
    def operand_count(self):
        return self._ptr.getNumOperands()

    @property
    def operands(self):
        """Yields operands of this instruction."""
        return [Value(self._ptr.getOperand(i))
                for i in range(self.operand_count)]

    def _get_operand(self, i):
        return _make_value(_core.LLVMUserGetOperand(self._ptr, i))

class Constant(User):

    @staticmethod
    def null(ty):
        return Value(api.llvm.Constant.getNullValue(ty._ptr))

    @staticmethod
    def all_ones(ty):
        return Value(api.llvm.Constant.getAllOnesValue(ty._ptr))

    @staticmethod
    def undef(ty):
        return Value(api.llvm.UndefValue.get(ty._ptr))

    @staticmethod
    def int(ty, value):
        return Value(api.llvm.ConstantInt.get(ty._ptr, value, False))

    @staticmethod
    def int_signextend(ty, value):
        return Value(api.llvm.ConstantInt.get(ty._ptr, value, True))

    @staticmethod
    def real(ty, value):
        return Value(api.llvm.ConstantFP.get(ty._ptr, value))

    @staticmethod
    def string(strval): # dont_null_terminate=True
        return Value(api.llvm.ConstantDataArray.getString(strval, False))

    @staticmethod
    def stringz(strval): # dont_null_terminate=False
        return Value(api.llvm.ConstantDataArray.getString(strval, True))

    @staticmethod
    def array(ty, consts):
        return Value(api.llvm.ConstantArray.get(ty._ptr, consts))

    @staticmethod
    def struct(consts): # not packed
        return Value(api.llvm.ConstantStruct.getAnon(llvm._extract_ptrs(consts),
                                                False))

    @staticmethod
    def packed_struct(consts):
         return Value(api.llvm.ConstantStruct.getAnon(llvm._extract_ptrs(consts),
                                                 False))

    @staticmethod
    def vector(consts):
        return Value(api.llvm.ConstantVector.get(llvm._extract_ptrs(consts)))

    @staticmethod
    def sizeof(ty):
        return Value(api.llvm.ConstantExpr.getSizeOf(ty._ptr))

    def neg(self):
        return Value(api.llvm.ConstantExpr.getNeg(self._ptr))

    def not_(self):
        return Value(api.llvm.ConstantExpr.getNot(self._ptr))

    def add(self, rhs):
        return Value(api.llvm.ConstantExpr.getAdd(self._ptr, rhs._ptr))

    def fadd(self, rhs):
        return Value(api.llvm.ConstantExpr.getFAdd(self._ptr, rhs._ptr))

    def sub(self, rhs):
        return Value(api.llvm.ConstantExpr.getSub(self._ptr, rhs._ptr))

    def fsub(self, rhs):
        return Value(api.llvm.ConstantExpr.getFSub(self._ptr, rhs._ptr))

    def mul(self, rhs):
        return Value(api.llvm.ConstantExpr.getMul(self._ptr, rhs._ptr))

    def fmul(self, rhs):
        return Value(api.llvm.ConstantExpr.getFMul(self._ptr, rhs._ptr))

    def udiv(self, rhs):
        return Value(api.llvm.ConstantExpr.getUDiv(self._ptr, rhs._ptr))

    def sdiv(self, rhs):
        return Value(api.llvm.ConstantExpr.getSDiv(self._ptr, rhs._ptr))

    def fdiv(self, rhs):
        return Value(api.llvm.ConstantExpr.getFDiv(self._ptr, rhs._ptr))

    def urem(self, rhs):
        return Value(api.llvm.ConstantExpr.getURem(self._ptr, rhs._ptr))

    def srem(self, rhs):
        return Value(api.llvm.ConstantExpr.getSRem(self._ptr, rhs._ptr))

    def frem(self, rhs):
        return Value(api.llvm.ConstantExpr.getFRem(self._ptr, rhs._ptr))

    def and_(self, rhs):
        return Value(api.llvm.ConstantExpr.getAnd(self._ptr, rhs._ptr))

    def or_(self, rhs):
        return Value(api.llvm.ConstantExpr.getOr(self._ptr, rhs._ptr))

    def xor(self, rhs):
        return Value(api.llvm.ConstantExpr.getXor(self._ptr, rhs._ptr))

    def icmp(self, int_pred, rhs):
        return Value(api.llvm.ConstantExpr.getICmp(int_pred, self._ptr, rhs._ptr))

    def fcmp(self, real_pred, rhs):
        return Value(api.llvm.ConstantExpr.getFCmp(real_pred, self._ptr, rhs._ptr))

    def shl(self, rhs):
        return Value(api.llvm.ConstantExpr.getShl(self._ptr, rhs._ptr))

    def lshr(self, rhs):
        return Value(api.llvm.ConstantExpr.getLShr(self._ptr, rhs._ptr))

    def ashr(self, rhs):
        return Value(api.llvm.ConstantExpr.getAShr(self._ptr, rhs._ptr))

    def gep(self, indices):
        indices = llvm._extract_ptrs(indices)
        return Value(api.llvm.ConstantExpr.getGetElementPtr(self._ptr, indices))

    def trunc(self, ty):
        return Value(api.llvm.ConstantExpr.getTrunc(self._ptr, ty))

    def sext(self, ty):
        return Value(api.llvm.ConstantExpr.getSExt(self._ptr, ty))

    def zext(self, ty):
        return Value(api.llvm.ConstantExpr.getZExt(self._ptr, ty))

    def fptrunc(self, ty):
        return Value(api.llvm.ConstantExpr.getFPTrunc(self._ptr, ty))

    def fpext(self, ty):
        return Value(api.llvm.ConstantExpr.getFPExtend(self._ptr, ty))

    def uitofp(self, ty):
        return Value(api.llvm.ConstantExpr.getUIToFP(self._ptr, ty))

    def sitofp(self, ty):
        return Value(api.llvm.ConstantExpr.getSIToFP(self._ptr, ty))

    def fptoui(self, ty):
        return Value(api.llvm.ConstantExpr.getFPToUI(self._ptr, ty))

    def fptosi(self, ty):
        return Value(api.llvm.ConstantExpr.getFPToSI(self._ptr, ty))

    def ptrtoint(self, ty):
        return Value(api.llvm.ConstantExpr.getPtrToInt(self._ptr, ty))

    def inttoptr(self, ty):
        return Value(api.llvm.ConstantExpr.getIntToPtr(self._ptr, ty))

    def bitcast(self, ty):
        return Value(api.llvm.ConstantExpr.getBitCast(self._ptr, ty))

    def select(self, true_const, false_const):
        return Value(api.llvm.ConstantExpr.getSelect(self._ptr,
                                                true_const._ptr,
                                                false_const._ptr))

    def extract_element(self, index): # note: self must be a _vector_ constant
        return Value(api.llvm.ConstantExpr.getExtractElement(self._ptr, index._ptr))

    def insert_element(self, value, index):
        return Value(api.llvm.ConstantExpr.getExtractElement(self._ptr,
                                                        value._ptr,
                                                        index._ptr))

    def shuffle_vector(self, vector_b, mask):
        return Value(api.llvm.ConstantExpr.getShuffleVector(self._ptr,
                                                       vector_b._ptr,
                                                       mask._ptr))

class ConstantExpr(Constant):
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

    @staticmethod
    def new(module, ty, name, addrspace=0):
        linkage = api.llvm.GlobalValue.LinkageTypes
        external_linkage = linkage.ExternalLinkage
        tlmode = api.llvm.GlobalVariable.ThreadLocalMode
        not_threadlocal = tlmode.NotThreadLocal
        gv = api.llvm.GlobalVariablel.new(module._ptr,
                                     ty._ptr,
                                     False, # is constant
                                     external_linkage,
                                     None, # initializer
                                     name,
                                     None, # insert before
                                     not_threadlocal,
                                     addrspace)
        return GlobalVariable(gv)

    @staticmethod
    def get(module, name):
        gv = GlobalVariable(module._ptr.getNamedGlobal(name))
        if not gv:
            llvm.LLVMException("no global named `%s`" % name)
        return gv

    def delete(self):
        self._ptr.eraseFromParent()

    def _get_initializer(self):
        if not self._ptr.hasInitializer():
            return None
        return Constant(self._ptr.getInitializer())

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

    def add_attribute(self, attr):
        attrbldr = api.llvm.AttrBuilder()
        attrbldr.addAttribute(attr)
        attrs = api.llvm.Attributes.get(context, attrbldr)
        self._ptr.addAttr(attrs)

    def remove_attribute(self, attr):
        attrbldr = api.llvm.AttrBuilder()
        attrbldr.addAttribute(attr)
        attrs = api.llvm.Attributes.get(context, attrbldr)
        self._ptr.removeAttr(attrs)

    def _set_alignment(self, align):
        attrbldr = api.llvm.AttrBuilder()
        attrbldr.addAlignmentAttr(align)
        attrs = api.llvm.Attributes.get(context, attrbldr)
        self._ptr.addAttr(attrs)

    def _get_alignment(self):
        return self._ptr.getParamAlignment()

    alignment = property(_get_alignment,
                         _set_alignment)

class Function(GlobalValue):

    @staticmethod
    def new(module, func_ty, name):
        return module.add_function(func_ty, name)

    @staticmethod
    def get_or_insert(module, func_ty, name):
        return module.get_or_insert_function(func_ty, name)

    @staticmethod
    def get(module, name):
        return module.get_function_named(name)

    @staticmethod
    def intrinsic(module, intrinsic_id, types):
        fn = api.llvm.Intrinsic.getDeclaration(module._ptr,
                                          intrinsic_id,
                                          types)
        return Function(fn)

    def delete(self):
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
        self._ptr.setDoesNotThow()

    does_not_throw = property(_get_does_not_throw, _set_does_not_throw)

    @property
    def args(self):
        return self._ptr.getArgumentList()

    @property
    def basic_block_count(self):
        return len(self.basic_blocks)

    @property
    def entry_basic_block(self):
        return self._ptr.getEntryBlock()

    def append_basic_block(self, name):
        context = api.llvm.getGlobalContext()
        bb = api.llvm.BasicBlock.Create(context, name, self._ptr, None)
        return BasicBlock(bb)

    @property
    def basic_blocks(self):
        return self._ptr.getBasicBlockList()
    
    def viewCFG(self):
        return self._ptr.viewCFG()

    def add_attribute(self, attr):
        _core.LLVMAddFunctionAttr(self._ptr, attr)

    def remove_attribute(self, attr):
        attrbldr = api.llvm.AttrBuilder()
        attrbldr.addAttribute(attr)
        attrs = api.llvm.Attributes.get(context, attrbldr)
        self._ptr.removeFnAttr(attrs)

    def viewCFGOnly(self):
        return self._ptr.viewCFGOnly()

    def verify(self):
        # Although we're just asking LLVM to return the success or
        # failure, it appears to print result to stderr and abort.
        
        # Note: LLVM has a bug in preverifier that will always abort
        #       the process upon failure.
        return api.llvm.verifyFunction()

#===----------------------------------------------------------------------===
# InlineAsm
#===----------------------------------------------------------------------===

class InlineAsm(Value):
    @staticmethod
    def get(functype, asm, constrains, side_effect=False,
            align_stack=False, dialect=api.llvm.InlineAsm.AsmDialect.AD_ATT):
        ilasm = api.llvm.InlineAsm.get(functype._ptr, asm, contrains, side_effect,
                                  align_stack, dialect)
        return InlineAsm(ilasm)

#===----------------------------------------------------------------------===
# MetaData
#===----------------------------------------------------------------------===

class MetaData(Value):
    @staticmethod
    def get(module, values):
        '''
        values -- must be an iterable of Constant or None. None is treated as "null".
        '''
        context = api.llvm.getGlobalContext()
        ptr = api.llvm.MDNode.get(context, llvm._extract_ptrs(values))
        return MetaData(ptr)

    @staticmethod
    def get_named_operands(module, name):
        namedmd = module.get_named_metadata(name)._ptr
        return [MetaData(namedmd.getOperand(i))
                for i in namedmd.getNumOperands()]

    @staticmethod
    def add_named_operand(module, name, operand):
        namedmd = module.get_or_insert_named_metadata(name)._ptr
        namedmd.addOperand(operand._ptr)

    @property
    def operand_count(self):
        return self._ptr.getOperand()

    @property
    def operands(self):
        """Yields operands of this metadata."""
        return [Value(self._ptr.getOperand(i)) for i in self.operand_count]


class MetaDataString(Value):
    @staticmethod
    def get(module, s):
        context = api.llvm.getGlobalContext()
        ptr = api.llvm.MDString.get(context, s)
        return MetaDataString(ptr)

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

    @property
    def basic_block(self):
        return BasicBlock(self._ptr.getParent())

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

    @property
    def opcode(self):
        return self._ptr.getOpcode()

    @property
    def opcode_name(self):
        return self._ptr.getOpcodeName()

    def erase_from_parent(self):
        return self._ptr.eraseFromParent()


class CallOrInvokeInstruction(Instruction):

    def _get_cc(self):
        return self._ptr.getCallingConv()

    def _set_cc(self, value):
        return self._ptr.setCallingConv(value)

    calling_convention = property(_get_cc, _set_cc)

    def add_parameter_attribute(self, idx, attr):
        attrbldr = api.llvm.AttrBuilder()
        attrbldr.addAttribute(attr)
        attrs = api.llvm.Attributes.get(context, attrbldr)
        self._ptr.addAttribute(idx, attrs)

    def remove_parameter_attribute(self, idx, attr):
        attrbldr = api.llvm.AttrBuilder()
        attrbldr.addAttribute(attr)
        attrs = api.llvm.Attributes.get(context, attrbldr)
        self._ptr.removeAttribute(idx, attrs)

    def set_parameter_alignment(self, idx, align):
        attrbldr = api.llvm.AttrBuilder()
        attrbldr.addAlignmentAttr(align)
        attrs = api.llvm.Attributes.get(context, attrbldr)
        self._ptr.addAttribute(idx, attrs)

    def _get_called_function(self):
        function = self._ptr.getCalledFunction()
        if function: # Return value can be None on indirect call/invoke
            return Value(function)

    def _set_called_function(self, function):
        self._ptr.setCalledFunction(function)

    called_function = property(_get_called_function, _set_called_function)


class PHINode(Instruction):

    @property
    def incoming_count(self):
        return self._ptr.getNumIncomingValues()

    def add_incoming(self, value, block):
        self._ptr.addIncoming(value._ptr, block._ptr)

    def get_incoming_value(self, idx):
        return self._ptr.getIncomingValue(idx)

    def get_incoming_block(self, idx):
        return self._ptr.getIncomingBlock(idx)


class SwitchInstruction(Instruction):

    def add_case(self, const, bblk):
        self._ptr.addCase(const._ptr, bblk._ptr)


class CompareInstruction(Instruction):

    @property
    def predicate(self):
        return self._ptr.getPredicate()


#===----------------------------------------------------------------------===
# Basic block
#===----------------------------------------------------------------------===

class BasicBlock(Value):

    def insert_before(self, name):
        context = api.llvm.getGlobalContext()
        ptr = api.llvm.BasicBlock.Create(context, name, self.function._ptr,
                                    self._ptr)
        return BasicBlock(ptr)

    def delete(self):
        self._ptr.eraseFromParent()

    @property
    def function(self):
        return Function(self._ptr.getParent())

    @property
    def instructions(self):
        return map(Value, self._ptr.getInstList())


#===----------------------------------------------------------------------===
# Builder
#===----------------------------------------------------------------------===

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
        instrs = bblk._ptr.getInstList()
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
        return BasicBlock(self._ptr.GetInsertBlock())

    # terminator instructions

    def ret_void(self):
        return Value(self._ptr.CreateRetVoid())
    
    def ret(self, value):
        return Value(self._ptr.CreateRet(value._ptr))

    def ret_many(self, values):
        values = llvm._extract_ptrs(values)
        return Value(self._ptr.CreateAggregateRet(values, len(values)))

    def branch(self, bblk):
        if __debug__:
            for instr in self.basic_block.instructions:
                assert not instr.is_terminator, "BasicBlock can only have one terminator"
        return Value(self._ptr.CreateBr(bblk._ptr))

    def cbranch(self, if_value, then_blk, else_blk):
        return Value(self._ptr.CreateCondBr(if_value._ptr,
                                            then_blk._ptr,
                                            else_blk._ptr))

    def switch(self, value, else_blk, n=10):
        return Value(self._ptr.CreateSwitch(self.value._ptr,
                                            self.else_blk._ptr,
                                            n))

    def invoke(self, func, args, then_blk, catch_blk, name=""):
        return Value(self._ptr.CreateInvoke(self.func._ptr,
                                            self.then_blk._ptr,
                                            self.catch_blk._ptr,
                                            args))

    def unreachable(self):
        return Value(self._ptr.CreateUnreachable())

    # arithmethic, bitwise and logical

    def add(self, lhs, rhs, name=""):
        return Value(self._ptr.CreateAdd(lhs._ptr, rhs._ptr, name))

    def fadd(self, lhs, rhs, name=""):
        return Value(self._ptr.CreateFAdd(lhs._ptr, rhs._ptr, name))

    def sub(self, lhs, rhs, name=""):
        return Value(self._ptr.CreateSub(lhs._ptr, rhs._ptr, name))

    def fsub(self, lhs, rhs, name=""):
        return Value(self._ptr.CreateFSub(lhs._ptr, rhs._ptr, name))

    def mul(self, lhs, rhs, name=""):
        return Value(self._ptr.CreateMul(lhs._ptr, rhs._ptr, name))

    def fmul(self, lhs, rhs, name=""):
        return Value(self._ptr.CreateFMul(lhs._ptr, rhs._ptr, name))

    def udiv(self, lhs, rhs, name=""):
        return Value(self._ptr.CreateUDiv(lhs._ptr, rhs._ptr, name))

    def sdiv(self, lhs, rhs, name=""):
        return Value(self._ptr.CreateSDiv(lhs._ptr, rhs._ptr, name))

    def fdiv(self, lhs, rhs, name=""):
        return Value(self._ptr.CreateFDiv(lhs._ptr, rhs._ptr, name))

    def urem(self, lhs, rhs, name=""):
        return Value(self._ptr.CreateURem(lhs._ptr, rhs._ptr, name))

    def srem(self, lhs, rhs, name=""):
        return Value(self._ptr.CreateSRem(lhs._ptr, rhs._ptr, name))

    def frem(self, lhs, rhs, name=""):
        return Value(self._ptr.CreateFRem(lhs._ptr, rhs._ptr, name))

    def shl(self, lhs, rhs, name=""):
        return Value(self._ptr.CreateShl(lhs._ptr, rhs._ptr, name))

    def lshr(self, lhs, rhs, name=""):
        return Value(self._ptr.CreateLShr(lhs._ptr, rhs._ptr, name))

    def ashr(self, lhs, rhs, name=""):
        return Value(self._ptr.CreateAShr(lhs._ptr, rhs._ptr, name))

    def and_(self, lhs, rhs, name=""):
        return Value(self._ptr.CreateAnd(lhs._ptr, rhs._ptr, name))

    def or_(self, lhs, rhs, name=""):
        return Value(self._ptr.CreateOr(lhs._ptr, rhs._ptr, name))

    def xor(self, lhs, rhs, name=""):
        return Value(self._ptr.CreateXor(lhs._ptr, rhs._ptr, name))

    def neg(self, val, name=""):
        return Value(self._ptr.CreateNeg(val._ptr, name))

    def not_(self, val, name=""):
        return Value(self._ptr.CreateNot(val._ptr, name))

    # memory

    def malloc(self, ty, name=""):
        context = api.llvm.getGlobalContext()
        intty = api.llvm.Type.getInt32Ty(context)
        sizeof = api.llvm.ConstantExpr.getSizeOf(ty)
        zero = api.llvm.ConstantInt.get(intty, 0)
        # XXX: how do I know when to insert?
        #      assume to end of block for now
        inst = api.llvm.CallInst.CreateMalloc(self.basic_block._ptr,
                                         intty,
                                         ty._ptr,
                                         sizeof,
                                         zero,
                                         None,
                                         name)
        return Value(inst)

    def malloc_array(self, ty, size, name=""):
        sizeof = api.llvm.ConstantExpr.getSizeOf(ty)
        # XXX: how do I know when to insert?
        #      assume to end of block for now
        inst = api.llvm.CallInst.CreateMalloc(self.basic_block._ptr,
                                         size.type._ptr,
                                         ty._ptr,
                                         sizeof,
                                         size._ptr,
                                         None,
                                         name)
        return Value(inst)

    def alloca(self, ty, name=""):
        zero = api.llvm.ConstantInt.get(intty, 0)
        return Value(self._ptr.CreateAlloca(ty._ptr, zero, name))

    def alloca_array(self, ty, size, name=""):
        return Value(self._ptr.CreateAlloca(ty._ptr, size._ptr, name))

    def free(self, ptr):
        return Value(api.llvm.CallInst.CreateFree(ptr._ptr, self.basic_block._ptr))

    def load(self, ptr, name="", align=0, volatile=False, invariant=False):
        inst = Value(self._ptr.CreateLoad(ptr._ptr, name))
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
        inst = Value(self._ptr.CreateStore(value._ptr, ptr._ptr))
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
        return Value(ret)

    # casts and extensions

    def trunc(self, value, dest_ty, name=""):
        return Value(self._ptr.CreateTrunc(value._ptr, dest_ty._ptr, name))

    def zext(self, value, dest_ty, name=""):
        return Value(self._ptr.CreateZext(value._ptr, dest_ty._ptr, name))

    def sext(self, value, dest_ty, name=""):
        return Value(self._ptr.CreateSext(value._ptr, dest_ty._ptr, name))

    def fptoui(self, value, dest_ty, name=""):
        return Value(self._ptr.CreateFPToUI(value._ptr, dest_ty._ptr, name))

    def fptosi(self, value, dest_ty, name=""):
        return Value(self._ptr.CreateFPToSI(value._ptr, dest_ty._ptr, name))

    def uitofp(self, value, dest_ty, name=""):
        return Value(self._ptr.CreateUIToFP(value._ptr, dest_ty._ptr, name))

    def sitofp(self, value, dest_ty, name=""):
        return Value(self._ptr.CreateSIToFP(value._ptr, dest_ty._ptr, name))

    def fptrunc(self, value, dest_ty, name=""):
        return Value(self._ptr.CreateFPTrunc(value._ptr, dest_ty._ptr, name))

    def fpext(self, value, dest_ty, name=""):
        return Value(self._ptr.CreateFPExt(value._ptr, dest_ty._ptr, name))

    def ptrtoint(self, value, dest_ty, name=""):
        return Value(self._ptr.CreatePtrToInt(value._ptr, dest_ty._ptr, name))

    def inttoptr(self, value, dest_ty, name=""):
        return Value(self._ptr.CreateIntToPtr(value._ptr, dest_ty._ptr, name))

    def bitcast(self, value, dest_ty, name=""):
        return Value(self._ptr.CreateBitCast(value._ptr, dest_ty._ptr, name))

    # comparisons

    def icmp(self, ipred, lhs, rhs, name=""):
        return Value(self._ptr.CreateICmp(ipred, lhs._ptr, rhs._ptr, name))

    def fcmp(self, rpred, lhs, rhs, name=""):
        return Value(self._ptr.CreateFCmp(rpred, lhs._ptr, rhs._ptr, name))

    # misc

    def extract_value(self, retval, idx, name=""):
        return Value(self._ptr.CreateExtractValue(retval._ptr, [idx], name))

    # obsolete synonym for extract_value
    getresult = extract_value

    def insert_value(self, retval, rhs, idx, name=""):
        return Value(self._ptr.CreateInsertValue(retval._ptr,
                                                rhs._ptr,
                                                [idx],
                                                name))

    def phi(self, ty, name=""):
        return Value(self._ptr.CreatePHI(ty._ptr, 2, name))

    def call(self, fn, args, name=""):
        err_template = 'Argument type mismatch: expected %s but got %s'
        for i, (t, v) in enumerate(zip(fn.type.pointee.args, args)):
            if  t != v.type:
                raise TypeError(err_template % (t, v.type))
        arg_ptrs = llvm._extract_ptrs(args)
        return Value(self._ptr.CreateCall(fn._ptr, arg_ptrs, name))

    def select(self, cond, then_value, else_value, name=""):
        return Value(self._ptr.CreateSelect(cond._ptr, then_value._ptr,
                                            else_value._ptr, name))

    def vaarg(self, list_val, ty, name=""):
        return Value(self._ptr.CreateVAArg(list_val._ptr, ty._ptr, name))

    def extract_element(self, vec_val, idx_val, name=""):
        return Value(self._ptr.CreateExtractElement(vec_val._ptr,
                                                    idx_val_.ptr,
                                                    name))


    def insert_element(self, vec_val, elt_val, idx_val, name=""):
        return Value(self._ptr.CreateExtractElement(vec_val._ptr,
                                                    elt_val._ptr,
                                                    idx_val_.ptr,
                                                    name))

    def shuffle_vector(self, vecA, vecB, mask, name=""):
        return Value(self._ptr.CreateShuffleVector(vecA._ptr,
                                                   vecB._ptr,
                                                   mask._ptr,
                                                   name))
    # atomics

    def atomic_cmpxchg(self, ptr, old, new, ordering, crossthread=True):
        return Value(self._ptr.CreateAtomicCmpXchg(ptr._ptr,
                                                   old._ptr,
                                                   new._ptr,
                                                   ordering,
                                                   _sync_scope(crossthread)))

    def atomic_rmw(self, op, ptr, val, ordering, crossthread=True):
        op_dict = dict((k.lower(), v)
                       for k, v in vars(api.llvm.AtomicRMWInst.BinOp))
        op = op_dict[op]
        return Value(self._ptr.CreateAtomicRMW(op, ptr._ptr, val._ptr,
                                               ordering,
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
        inst = self._ptr.load(ptr, align=align, volatile=volatile, name=name)
        inst._ptr.setAtomic(ordering, _sync_scope(crossthread))
        return inst

    def atomic_store(self, value, ptr, ordering, align=1, crossthread=True,
                     volatile=False):
        inst = self._ptr.store(ptr, value, align=align, volatile=volatile,
                               name=name)
        inst._ptr.setAtomic(ordering, _sync_scope(crossthread))
        return inst


    def fence(self, ordering, crossthread=True):
        return Value(self._ptr.CreateFence(ordering,
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
    with contextlib.closing(StringIO()) as errmsg:
        failed = api.llvm.sys.LoadLibraryPermanently(filename, errmsg)
        if failed:
            raise llvm.LLVMException(errmsg.getvalue())

def inline_function(call):
    info = api.llvm.InlineFunctionInfo()
    return api.llvm.InlineFunction(call._ptr, info)

def parse_environment_options(progname, envname):
    api.llvm.cl.ParseEnvironmentOptions(progname, envname)

if api.llvm.InitializeNativeTarget():
    raise llvm.LLVMException("No native target!?")
if api.llvm.InitializeNativeTargetAsmPrinter():
    # should this be an optional feature?
    # should user trigger the initialization?
    raise llvm.LLVMException("No native asm printer!?")

#===----------------------------------------------------------------------===
# Initialization
#===----------------------------------------------------------------------===

HAS_PTX = HAS_NVPTX = False

if True: # use PTX?
    try:
        api.LLVMInitializePTXTarget()
        api.LLVMInitializePTXTargetInfo()
        api.LLVMInitializePTXTargetMC()
        api.LLVMInitializePTXAsmPrinter()
        HAS_PTX = True
    except AttributeError:
        try:
            api.LLVMInitializeNVPTXTarget()
            api.LLVMInitializeNVPTXTargetInfo()
            api.LLVMInitializeNVPTXTargetMC()
            api.LLVMInitializeNVPTXAsmPrinter()
            HAS_NVPTX = True
        except AttributeError:
            pass



