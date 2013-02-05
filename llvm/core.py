try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import api

#===----------------------------------------------------------------------===
# Enumerations
#===----------------------------------------------------------------------===

# type kinds (LLVMTypeKind enum)
TYPE_VOID       = 0
TYPE_HALF       = 1
TYPE_FLOAT      = 2
TYPE_DOUBLE     = 3
TYPE_X86_FP80   = 4
TYPE_FP128      = 5
TYPE_PPC_FP128  = 6
TYPE_LABEL      = 7
TYPE_INTEGER    = 8
TYPE_FUNCTION   = 9
TYPE_STRUCT     = 10
TYPE_ARRAY      = 11
TYPE_POINTER    = 12
TYPE_VECTOR     = 13
TYPE_METADATA   = 14
TYPE_X86_MMX    = 15


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
VALUE_CONSTANT_DATA_ARRAY               = 9
VALUE_CONSTANT_DATA_VECTOR              = 10
VALUE_CONSTANT_INT                      = 11
VALUE_CONSTANT_FP                       = 12
VALUE_CONSTANT_ARRAY                    = 13
VALUE_CONSTANT_STRUCT                   = 14
VALUE_CONSTANT_VECTOR                   = 15
VALUE_CONSTANT_POINTER_NULL             = 16
VALUE_MD_NODE                           = 17
VALUE_MD_STRING                         = 18
VALUE_INLINE_ASM                        = 19
VALUE_PSEUDO_SOURCE_VALUE               = 20
VALUE_FIXED_STACK_PSEUDO_SOURCE_VALUE   = 21
VALUE_INSTRUCTION                       = 22

# instruction opcodes (from include/llvm/Instruction.def)
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

# calling conventions
CC_C             = 0
CC_FASTCALL      = 8
CC_COLDCALL      = 9
CC_GHC           = 10
CC_X86_STDCALL   = 64
CC_X86_FASTCALL  = 65
CC_ARM_APCS      = 66
CC_ARM_AAPCS     = 67
CC_ARM_AAPCS_VFP = 68
CC_MSP430_INTR   = 69
CC_X86_THISCALL  = 70
CC_PTX_KERNEL    = 71
CC_PTX_DEVICE    = 72
CC_MBLAZE_INTR   = 73
CC_MBLAZE_SVOL   = 74


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
ATTR_ALIGNMENT          = 1<<16
ATTR_NO_CAPTURE         = 1<<21
ATTR_NO_REDZONE         = 1<<22
ATTR_NO_IMPLICIT_FLOAT  = 1<<23
ATTR_NAKED              = 1<<24
ATTR_INLINE_HINT        = 1<<25
ATTR_STACK_ALIGNMENT    = 7<<26
ATTR_HOTPATCH           = 1<<29

class Module(object):
    @staticmethod
    def new(id):
        """Create a new Module instance.

        Creates an instance of Module, having the id `id'.
        """
        context = api.getGlobalContext()
        m = api.Module.new(id, context)
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
        m = api.ParseBitCodeFile(bc, context, errbuf)
        if not m:
            raise Exception(errbuf.getvalue())
        errbuf.close()
        return Module(m)

    def __init__(self, ptr):
        self.ptr = ptr


    