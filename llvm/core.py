# 
# Copyright (c) 2008, Mahadevan R All rights reserved.
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
from llvm._util import *    # utility functions
import weakref              # global list of modules


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

# value IDs (llvm::Value::ValueTy enum)
VALUE_ARGUMENT                  = 0
VALUE_BASIC_BLOCK               = 1
VALUE_FUNCTION                  = 2
VALUE_GLOBAL_ALIAS              = 3
VALUE_GLOBAL_VARIABLE           = 4
VALUE_UNDEF_VALUE               = 5
VALUE_CONSTANT_EXPR             = 6
VALUE_CONSTANT_AGGREGATE_ZERO   = 7
VALUE_CONSTANT_INT              = 8
VALUE_CONSTANT_FP               = 9
VALUE_CONSTANT_ARRAY            = 10
VALUE_CONSTANT_STRUCT           = 11
VALUE_CONSTANT_VECTOR           = 12
VALUE_CONSTANT_POINTER_NULL     = 13
VALUE_INLINE_ASM                = 14
VALUE_PSEUDO_SOURCE_VALUE       = 15
VALUE_INSTRUCTION               = 16

# instruction opcodes
OPCODE_RET            = 1
OPCODE_BR             = 2
OPCODE_SWITCH         = 3
OPCODE_INVOKE         = 4
OPCODE_UNWIND         = 5
OPCODE_UNREACHABLE    = 6
OPCODE_ADD            = 7
OPCODE_SUB            = 8
OPCODE_MUL            = 9
OPCODE_UDIV           = 10
OPCODE_SDIV           = 11
OPCODE_FDIV           = 12
OPCODE_UREM           = 13
OPCODE_SREM           = 14
OPCODE_FREM           = 15
OPCODE_SHL            = 16
OPCODE_LSHR           = 17
OPCODE_ASHR           = 18
OPCODE_AND            = 19
OPCODE_OR             = 20
OPCODE_XOR            = 21
OPCODE_MALLOC         = 22
OPCODE_FREE           = 23
OPCODE_ALLOCA         = 24
OPCODE_LOAD           = 25
OPCODE_STORE          = 26
OPCODE_GETELEMENTPTR  = 27
OPCODE_TRUNC          = 28
OPCODE_ZEXT           = 29
OPCODE_SZEXT          = 30
OPCODE_FPTOUI         = 31
OPCODE_FPTOSI         = 32
OPCODE_UITOFP         = 33
OPCODE_SITOFP         = 34
OPCODE_FPTRUNC        = 35
OPCODE_FPEXT          = 36
OPCODE_PTRTOINT       = 37
OPCODE_INTTOPTR       = 38
OPCODE_BITCAST        = 39
OPCODE_ICMP           = 40
OPCODE_FCMP           = 41
OPCODE_PHI            = 42
OPCODE_CALL           = 43
OPCODE_SELECT         = 44
OPCODE_USEROP1        = 45
OPCODE_USEROP2        = 46
OPCODE_VAARG          = 47
OPCODE_EXTRACTELEMENT = 48
OPCODE_INSERTELEMENT  = 49
OPCODE_SHUFFLEVECTOR  = 50
OPCODE_EXTRACTVALUE   = 51
OPCODE_INSERTVALUE    = 52
OPCODE_VICMP          = 53
OPCODE_VFCMP          = 54

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
LINKAGE_COMMON      = 9

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

# intrinsic IDs
INTR_ALPHA_UMULH               = 1
INTR_ANNOTATION                = 2
INTR_ARM_THREAD_POINTER        = 3
INTR_ATOMIC_CMP_SWAP           = 4
INTR_ATOMIC_LOAD_ADD           = 5
INTR_ATOMIC_LOAD_AND           = 6
INTR_ATOMIC_LOAD_MAX           = 7
INTR_ATOMIC_LOAD_MIN           = 8
INTR_ATOMIC_LOAD_NAND          = 9
INTR_ATOMIC_LOAD_OR            = 10
INTR_ATOMIC_LOAD_SUB           = 11
INTR_ATOMIC_LOAD_UMAX          = 12
INTR_ATOMIC_LOAD_UMIN          = 13
INTR_ATOMIC_LOAD_XOR           = 14
INTR_ATOMIC_SWAP               = 15
INTR_BSWAP                     = 16
INTR_CONVERTFF                 = 17
INTR_CONVERTFSI                = 18
INTR_CONVERTFUI                = 19
INTR_CONVERTSIF                = 20
INTR_CONVERTSS                 = 21
INTR_CONVERTSU                 = 22
INTR_CONVERTUIF                = 23
INTR_CONVERTUS                 = 24
INTR_CONVERTUU                 = 25
INTR_COS                       = 26
INTR_CTLZ                      = 27
INTR_CTPOP                     = 28
INTR_CTTZ                      = 29
INTR_DBG_DECLARE               = 30
INTR_DBG_FUNC_START            = 31
INTR_DBG_REGION_END            = 32
INTR_DBG_REGION_START          = 33
INTR_DBG_STOPPOINT             = 34
INTR_EH_DWARF_CFA              = 35
INTR_EH_EXCEPTION              = 36
INTR_EH_RETURN_I32             = 37
INTR_EH_RETURN_I64             = 38
INTR_EH_SELECTOR_I32           = 39
INTR_EH_SELECTOR_I64           = 40
INTR_EH_TYPEID_FOR_I32         = 41
INTR_EH_TYPEID_FOR_I64         = 42
INTR_EH_UNWIND_INIT            = 43
INTR_EXP                       = 44
INTR_EXP2                      = 45
INTR_FLT_ROUNDS                = 46
INTR_FRAMEADDRESS              = 47
INTR_GCREAD                    = 48
INTR_GCROOT                    = 49
INTR_GCWRITE                   = 50
INTR_INIT_TRAMPOLINE           = 51
INTR_LOG                       = 52
INTR_LOG10                     = 53
INTR_LOG2                      = 54
INTR_LONGJMP                   = 55
INTR_MEMCPY                    = 56
INTR_MEMMOVE                   = 57
INTR_MEMORY_BARRIER            = 58
INTR_MEMSET                    = 59
INTR_PART_SELECT               = 60
INTR_PART_SET                  = 61
INTR_PCMARKER                  = 62
INTR_POW                       = 63
INTR_POWI                      = 64
INTR_PPC_ALTIVEC_DSS           = 65
INTR_PPC_ALTIVEC_DSSALL        = 66
INTR_PPC_ALTIVEC_DST           = 67
INTR_PPC_ALTIVEC_DSTST         = 68
INTR_PPC_ALTIVEC_DSTSTT        = 69
INTR_PPC_ALTIVEC_DSTT          = 70
INTR_PPC_ALTIVEC_LVEBX         = 71
INTR_PPC_ALTIVEC_LVEHX         = 72
INTR_PPC_ALTIVEC_LVEWX         = 73
INTR_PPC_ALTIVEC_LVSL          = 74
INTR_PPC_ALTIVEC_LVSR          = 75
INTR_PPC_ALTIVEC_LVX           = 76
INTR_PPC_ALTIVEC_LVXL          = 77
INTR_PPC_ALTIVEC_MFVSCR        = 78
INTR_PPC_ALTIVEC_MTVSCR        = 79
INTR_PPC_ALTIVEC_STVEBX        = 80
INTR_PPC_ALTIVEC_STVEHX        = 81
INTR_PPC_ALTIVEC_STVEWX        = 82
INTR_PPC_ALTIVEC_STVX          = 83
INTR_PPC_ALTIVEC_STVXL         = 84
INTR_PPC_ALTIVEC_VADDCUW       = 85
INTR_PPC_ALTIVEC_VADDSBS       = 86
INTR_PPC_ALTIVEC_VADDSHS       = 87
INTR_PPC_ALTIVEC_VADDSWS       = 88
INTR_PPC_ALTIVEC_VADDUBS       = 89
INTR_PPC_ALTIVEC_VADDUHS       = 90
INTR_PPC_ALTIVEC_VADDUWS       = 91
INTR_PPC_ALTIVEC_VAVGSB        = 92
INTR_PPC_ALTIVEC_VAVGSH        = 93
INTR_PPC_ALTIVEC_VAVGSW        = 94
INTR_PPC_ALTIVEC_VAVGUB        = 95
INTR_PPC_ALTIVEC_VAVGUH        = 96
INTR_PPC_ALTIVEC_VAVGUW        = 97
INTR_PPC_ALTIVEC_VCFSX         = 98
INTR_PPC_ALTIVEC_VCFUX         = 99
INTR_PPC_ALTIVEC_VCMPBFP       = 100
INTR_PPC_ALTIVEC_VCMPBFP_P     = 101
INTR_PPC_ALTIVEC_VCMPEQFP      = 102
INTR_PPC_ALTIVEC_VCMPEQFP_P    = 103
INTR_PPC_ALTIVEC_VCMPEQUB      = 104
INTR_PPC_ALTIVEC_VCMPEQUB_P    = 105
INTR_PPC_ALTIVEC_VCMPEQUH      = 106
INTR_PPC_ALTIVEC_VCMPEQUH_P    = 107
INTR_PPC_ALTIVEC_VCMPEQUW      = 108
INTR_PPC_ALTIVEC_VCMPEQUW_P    = 109
INTR_PPC_ALTIVEC_VCMPGEFP      = 110
INTR_PPC_ALTIVEC_VCMPGEFP_P    = 111
INTR_PPC_ALTIVEC_VCMPGTFP      = 112
INTR_PPC_ALTIVEC_VCMPGTFP_P    = 113
INTR_PPC_ALTIVEC_VCMPGTSB      = 114
INTR_PPC_ALTIVEC_VCMPGTSB_P    = 115
INTR_PPC_ALTIVEC_VCMPGTSH      = 116
INTR_PPC_ALTIVEC_VCMPGTSH_P    = 117
INTR_PPC_ALTIVEC_VCMPGTSW      = 118
INTR_PPC_ALTIVEC_VCMPGTSW_P    = 119
INTR_PPC_ALTIVEC_VCMPGTUB      = 120
INTR_PPC_ALTIVEC_VCMPGTUB_P    = 121
INTR_PPC_ALTIVEC_VCMPGTUH      = 122
INTR_PPC_ALTIVEC_VCMPGTUH_P    = 123
INTR_PPC_ALTIVEC_VCMPGTUW      = 124
INTR_PPC_ALTIVEC_VCMPGTUW_P    = 125
INTR_PPC_ALTIVEC_VCTSXS        = 126
INTR_PPC_ALTIVEC_VCTUXS        = 127
INTR_PPC_ALTIVEC_VEXPTEFP      = 128
INTR_PPC_ALTIVEC_VLOGEFP       = 129
INTR_PPC_ALTIVEC_VMADDFP       = 130
INTR_PPC_ALTIVEC_VMAXFP        = 131
INTR_PPC_ALTIVEC_VMAXSB        = 132
INTR_PPC_ALTIVEC_VMAXSH        = 133
INTR_PPC_ALTIVEC_VMAXSW        = 134
INTR_PPC_ALTIVEC_VMAXUB        = 135
INTR_PPC_ALTIVEC_VMAXUH        = 136
INTR_PPC_ALTIVEC_VMAXUW        = 137
INTR_PPC_ALTIVEC_VMHADDSHS     = 138
INTR_PPC_ALTIVEC_VMHRADDSHS    = 139
INTR_PPC_ALTIVEC_VMINFP        = 140
INTR_PPC_ALTIVEC_VMINSB        = 141
INTR_PPC_ALTIVEC_VMINSH        = 142
INTR_PPC_ALTIVEC_VMINSW        = 143
INTR_PPC_ALTIVEC_VMINUB        = 144
INTR_PPC_ALTIVEC_VMINUH        = 145
INTR_PPC_ALTIVEC_VMINUW        = 146
INTR_PPC_ALTIVEC_VMLADDUHM     = 147
INTR_PPC_ALTIVEC_VMSUMMBM      = 148
INTR_PPC_ALTIVEC_VMSUMSHM      = 149
INTR_PPC_ALTIVEC_VMSUMSHS      = 150
INTR_PPC_ALTIVEC_VMSUMUBM      = 151
INTR_PPC_ALTIVEC_VMSUMUHM      = 152
INTR_PPC_ALTIVEC_VMSUMUHS      = 153
INTR_PPC_ALTIVEC_VMULESB       = 154
INTR_PPC_ALTIVEC_VMULESH       = 155
INTR_PPC_ALTIVEC_VMULEUB       = 156
INTR_PPC_ALTIVEC_VMULEUH       = 157
INTR_PPC_ALTIVEC_VMULOSB       = 158
INTR_PPC_ALTIVEC_VMULOSH       = 159
INTR_PPC_ALTIVEC_VMULOUB       = 160
INTR_PPC_ALTIVEC_VMULOUH       = 161
INTR_PPC_ALTIVEC_VNMSUBFP      = 162
INTR_PPC_ALTIVEC_VPERM         = 163
INTR_PPC_ALTIVEC_VPKPX         = 164
INTR_PPC_ALTIVEC_VPKSHSS       = 165
INTR_PPC_ALTIVEC_VPKSHUS       = 166
INTR_PPC_ALTIVEC_VPKSWSS       = 167
INTR_PPC_ALTIVEC_VPKSWUS       = 168
INTR_PPC_ALTIVEC_VPKUHUS       = 169
INTR_PPC_ALTIVEC_VPKUWUS       = 170
INTR_PPC_ALTIVEC_VREFP         = 171
INTR_PPC_ALTIVEC_VRFIM         = 172
INTR_PPC_ALTIVEC_VRFIN         = 173
INTR_PPC_ALTIVEC_VRFIP         = 174
INTR_PPC_ALTIVEC_VRFIZ         = 175
INTR_PPC_ALTIVEC_VRLB          = 176
INTR_PPC_ALTIVEC_VRLH          = 177
INTR_PPC_ALTIVEC_VRLW          = 178
INTR_PPC_ALTIVEC_VRSQRTEFP     = 179
INTR_PPC_ALTIVEC_VSEL          = 180
INTR_PPC_ALTIVEC_VSL           = 181
INTR_PPC_ALTIVEC_VSLB          = 182
INTR_PPC_ALTIVEC_VSLH          = 183
INTR_PPC_ALTIVEC_VSLO          = 184
INTR_PPC_ALTIVEC_VSLW          = 185
INTR_PPC_ALTIVEC_VSR           = 186
INTR_PPC_ALTIVEC_VSRAB         = 187
INTR_PPC_ALTIVEC_VSRAH         = 188
INTR_PPC_ALTIVEC_VSRAW         = 189
INTR_PPC_ALTIVEC_VSRB          = 190
INTR_PPC_ALTIVEC_VSRH          = 191
INTR_PPC_ALTIVEC_VSRO          = 192
INTR_PPC_ALTIVEC_VSRW          = 193
INTR_PPC_ALTIVEC_VSUBCUW       = 194
INTR_PPC_ALTIVEC_VSUBSBS       = 195
INTR_PPC_ALTIVEC_VSUBSHS       = 196
INTR_PPC_ALTIVEC_VSUBSWS       = 197
INTR_PPC_ALTIVEC_VSUBUBS       = 198
INTR_PPC_ALTIVEC_VSUBUHS       = 199
INTR_PPC_ALTIVEC_VSUBUWS       = 200
INTR_PPC_ALTIVEC_VSUM2SWS      = 201
INTR_PPC_ALTIVEC_VSUM4SBS      = 202
INTR_PPC_ALTIVEC_VSUM4SHS      = 203
INTR_PPC_ALTIVEC_VSUM4UBS      = 204
INTR_PPC_ALTIVEC_VSUMSWS       = 205
INTR_PPC_ALTIVEC_VUPKHPX       = 206
INTR_PPC_ALTIVEC_VUPKHSB       = 207
INTR_PPC_ALTIVEC_VUPKHSH       = 208
INTR_PPC_ALTIVEC_VUPKLPX       = 209
INTR_PPC_ALTIVEC_VUPKLSB       = 210
INTR_PPC_ALTIVEC_VUPKLSH       = 211
INTR_PPC_DCBA                  = 212
INTR_PPC_DCBF                  = 213
INTR_PPC_DCBI                  = 214
INTR_PPC_DCBST                 = 215
INTR_PPC_DCBT                  = 216
INTR_PPC_DCBTST                = 217
INTR_PPC_DCBZ                  = 218
INTR_PPC_DCBZL                 = 219
INTR_PPC_SYNC                  = 220
INTR_PREFETCH                  = 221
INTR_PTR_ANNOTATION            = 222
INTR_READCYCLECOUNTER          = 223
INTR_RETURNADDRESS             = 224
INTR_SADD_WITH_OVERFLOW        = 225
INTR_SETJMP                    = 226
INTR_SIGLONGJMP                = 227
INTR_SIGSETJMP                 = 228
INTR_SIN                       = 229
INTR_SMUL_WITH_OVERFLOW        = 230
INTR_SPU_SI_A                  = 231
INTR_SPU_SI_ADDX               = 232
INTR_SPU_SI_AH                 = 233
INTR_SPU_SI_AHI                = 234
INTR_SPU_SI_AI                 = 235
INTR_SPU_SI_AND                = 236
INTR_SPU_SI_ANDBI              = 237
INTR_SPU_SI_ANDC               = 238
INTR_SPU_SI_ANDHI              = 239
INTR_SPU_SI_ANDI               = 240
INTR_SPU_SI_BG                 = 241
INTR_SPU_SI_BGX                = 242
INTR_SPU_SI_CEQ                = 243
INTR_SPU_SI_CEQB               = 244
INTR_SPU_SI_CEQBI              = 245
INTR_SPU_SI_CEQH               = 246
INTR_SPU_SI_CEQHI              = 247
INTR_SPU_SI_CEQI               = 248
INTR_SPU_SI_CG                 = 249
INTR_SPU_SI_CGT                = 250
INTR_SPU_SI_CGTB               = 251
INTR_SPU_SI_CGTBI              = 252
INTR_SPU_SI_CGTH               = 253
INTR_SPU_SI_CGTHI              = 254
INTR_SPU_SI_CGTI               = 255
INTR_SPU_SI_CGX                = 256
INTR_SPU_SI_CLGT               = 257
INTR_SPU_SI_CLGTB              = 258
INTR_SPU_SI_CLGTBI             = 259
INTR_SPU_SI_CLGTH              = 260
INTR_SPU_SI_CLGTHI             = 261
INTR_SPU_SI_CLGTI              = 262
INTR_SPU_SI_DFA                = 263
INTR_SPU_SI_DFM                = 264
INTR_SPU_SI_DFMA               = 265
INTR_SPU_SI_DFMS               = 266
INTR_SPU_SI_DFNMA              = 267
INTR_SPU_SI_DFNMS              = 268
INTR_SPU_SI_DFS                = 269
INTR_SPU_SI_FA                 = 270
INTR_SPU_SI_FCEQ               = 271
INTR_SPU_SI_FCGT               = 272
INTR_SPU_SI_FCMEQ              = 273
INTR_SPU_SI_FCMGT              = 274
INTR_SPU_SI_FM                 = 275
INTR_SPU_SI_FMA                = 276
INTR_SPU_SI_FMS                = 277
INTR_SPU_SI_FNMS               = 278
INTR_SPU_SI_FS                 = 279
INTR_SPU_SI_FSMBI              = 280
INTR_SPU_SI_MPY                = 281
INTR_SPU_SI_MPYA               = 282
INTR_SPU_SI_MPYH               = 283
INTR_SPU_SI_MPYHH              = 284
INTR_SPU_SI_MPYHHA             = 285
INTR_SPU_SI_MPYHHAU            = 286
INTR_SPU_SI_MPYHHU             = 287
INTR_SPU_SI_MPYI               = 288
INTR_SPU_SI_MPYS               = 289
INTR_SPU_SI_MPYU               = 290
INTR_SPU_SI_MPYUI              = 291
INTR_SPU_SI_NAND               = 292
INTR_SPU_SI_NOR                = 293
INTR_SPU_SI_OR                 = 294
INTR_SPU_SI_ORBI               = 295
INTR_SPU_SI_ORC                = 296
INTR_SPU_SI_ORHI               = 297
INTR_SPU_SI_ORI                = 298
INTR_SPU_SI_SF                 = 299
INTR_SPU_SI_SFH                = 300
INTR_SPU_SI_SFHI               = 301
INTR_SPU_SI_SFI                = 302
INTR_SPU_SI_SFX                = 303
INTR_SPU_SI_SHLI               = 304
INTR_SPU_SI_SHLQBI             = 305
INTR_SPU_SI_SHLQBII            = 306
INTR_SPU_SI_SHLQBY             = 307
INTR_SPU_SI_SHLQBYI            = 308
INTR_SPU_SI_XOR                = 309
INTR_SPU_SI_XORBI              = 310
INTR_SPU_SI_XORHI              = 311
INTR_SPU_SI_XORI               = 312
INTR_SQRT                      = 313
INTR_SSUB_WITH_OVERFLOW        = 314
INTR_STACKPROTECTOR            = 315
INTR_STACKRESTORE              = 316
INTR_STACKSAVE                 = 317
INTR_TRAP                      = 318
INTR_UADD_WITH_OVERFLOW        = 319
INTR_UMUL_WITH_OVERFLOW        = 320
INTR_USUB_WITH_OVERFLOW        = 321
INTR_VACOPY                    = 322
INTR_VAEND                     = 323
INTR_VAR_ANNOTATION            = 324
INTR_VASTART                   = 325
INTR_X86_MMX_EMMS              = 326
INTR_X86_MMX_FEMMS             = 327
INTR_X86_MMX_MASKMOVQ          = 328
INTR_X86_MMX_MOVNT_DQ          = 329
INTR_X86_MMX_PACKSSDW          = 330
INTR_X86_MMX_PACKSSWB          = 331
INTR_X86_MMX_PACKUSWB          = 332
INTR_X86_MMX_PADDS_B           = 333
INTR_X86_MMX_PADDS_W           = 334
INTR_X86_MMX_PADDUS_B          = 335
INTR_X86_MMX_PADDUS_W          = 336
INTR_X86_MMX_PAVG_B            = 337
INTR_X86_MMX_PAVG_W            = 338
INTR_X86_MMX_PCMPEQ_B          = 339
INTR_X86_MMX_PCMPEQ_D          = 340
INTR_X86_MMX_PCMPEQ_W          = 341
INTR_X86_MMX_PCMPGT_B          = 342
INTR_X86_MMX_PCMPGT_D          = 343
INTR_X86_MMX_PCMPGT_W          = 344
INTR_X86_MMX_PMADD_WD          = 345
INTR_X86_MMX_PMAXS_W           = 346
INTR_X86_MMX_PMAXU_B           = 347
INTR_X86_MMX_PMINS_W           = 348
INTR_X86_MMX_PMINU_B           = 349
INTR_X86_MMX_PMOVMSKB          = 350
INTR_X86_MMX_PMULH_W           = 351
INTR_X86_MMX_PMULHU_W          = 352
INTR_X86_MMX_PMULU_DQ          = 353
INTR_X86_MMX_PSAD_BW           = 354
INTR_X86_MMX_PSLL_D            = 355
INTR_X86_MMX_PSLL_Q            = 356
INTR_X86_MMX_PSLL_W            = 357
INTR_X86_MMX_PSLLI_D           = 358
INTR_X86_MMX_PSLLI_Q           = 359
INTR_X86_MMX_PSLLI_W           = 360
INTR_X86_MMX_PSRA_D            = 361
INTR_X86_MMX_PSRA_W            = 362
INTR_X86_MMX_PSRAI_D           = 363
INTR_X86_MMX_PSRAI_W           = 364
INTR_X86_MMX_PSRL_D            = 365
INTR_X86_MMX_PSRL_Q            = 366
INTR_X86_MMX_PSRL_W            = 367
INTR_X86_MMX_PSRLI_D           = 368
INTR_X86_MMX_PSRLI_Q           = 369
INTR_X86_MMX_PSRLI_W           = 370
INTR_X86_MMX_PSUBS_B           = 371
INTR_X86_MMX_PSUBS_W           = 372
INTR_X86_MMX_PSUBUS_B          = 373
INTR_X86_MMX_PSUBUS_W          = 374
INTR_X86_SSE2_ADD_SD           = 375
INTR_X86_SSE2_CLFLUSH          = 376
INTR_X86_SSE2_CMP_PD           = 377
INTR_X86_SSE2_CMP_SD           = 378
INTR_X86_SSE2_COMIEQ_SD        = 379
INTR_X86_SSE2_COMIGE_SD        = 380
INTR_X86_SSE2_COMIGT_SD        = 381
INTR_X86_SSE2_COMILE_SD        = 382
INTR_X86_SSE2_COMILT_SD        = 383
INTR_X86_SSE2_COMINEQ_SD       = 384
INTR_X86_SSE2_CVTDQ2PD         = 385
INTR_X86_SSE2_CVTDQ2PS         = 386
INTR_X86_SSE2_CVTPD2DQ         = 387
INTR_X86_SSE2_CVTPD2PS         = 388
INTR_X86_SSE2_CVTPS2DQ         = 389
INTR_X86_SSE2_CVTPS2PD         = 390
INTR_X86_SSE2_CVTSD2SI         = 391
INTR_X86_SSE2_CVTSD2SI64       = 392
INTR_X86_SSE2_CVTSD2SS         = 393
INTR_X86_SSE2_CVTSI2SD         = 394
INTR_X86_SSE2_CVTSI642SD       = 395
INTR_X86_SSE2_CVTSS2SD         = 396
INTR_X86_SSE2_CVTTPD2DQ        = 397
INTR_X86_SSE2_CVTTPS2DQ        = 398
INTR_X86_SSE2_CVTTSD2SI        = 399
INTR_X86_SSE2_CVTTSD2SI64      = 400
INTR_X86_SSE2_DIV_SD           = 401
INTR_X86_SSE2_LFENCE           = 402
INTR_X86_SSE2_LOADU_DQ         = 403
INTR_X86_SSE2_LOADU_PD         = 404
INTR_X86_SSE2_MASKMOV_DQU      = 405
INTR_X86_SSE2_MAX_PD           = 406
INTR_X86_SSE2_MAX_SD           = 407
INTR_X86_SSE2_MFENCE           = 408
INTR_X86_SSE2_MIN_PD           = 409
INTR_X86_SSE2_MIN_SD           = 410
INTR_X86_SSE2_MOVMSK_PD        = 411
INTR_X86_SSE2_MOVNT_DQ         = 412
INTR_X86_SSE2_MOVNT_I          = 413
INTR_X86_SSE2_MOVNT_PD         = 414
INTR_X86_SSE2_MUL_SD           = 415
INTR_X86_SSE2_PACKSSDW_128     = 416
INTR_X86_SSE2_PACKSSWB_128     = 417
INTR_X86_SSE2_PACKUSWB_128     = 418
INTR_X86_SSE2_PADDS_B          = 419
INTR_X86_SSE2_PADDS_W          = 420
INTR_X86_SSE2_PADDUS_B         = 421
INTR_X86_SSE2_PADDUS_W         = 422
INTR_X86_SSE2_PAVG_B           = 423
INTR_X86_SSE2_PAVG_W           = 424
INTR_X86_SSE2_PCMPEQ_B         = 425
INTR_X86_SSE2_PCMPEQ_D         = 426
INTR_X86_SSE2_PCMPEQ_W         = 427
INTR_X86_SSE2_PCMPGT_B         = 428
INTR_X86_SSE2_PCMPGT_D         = 429
INTR_X86_SSE2_PCMPGT_W         = 430
INTR_X86_SSE2_PMADD_WD         = 431
INTR_X86_SSE2_PMAXS_W          = 432
INTR_X86_SSE2_PMAXU_B          = 433
INTR_X86_SSE2_PMINS_W          = 434
INTR_X86_SSE2_PMINU_B          = 435
INTR_X86_SSE2_PMOVMSKB_128     = 436
INTR_X86_SSE2_PMULH_W          = 437
INTR_X86_SSE2_PMULHU_W         = 438
INTR_X86_SSE2_PMULU_DQ         = 439
INTR_X86_SSE2_PSAD_BW          = 440
INTR_X86_SSE2_PSLL_D           = 441
INTR_X86_SSE2_PSLL_DQ          = 442
INTR_X86_SSE2_PSLL_DQ_BS       = 443
INTR_X86_SSE2_PSLL_Q           = 444
INTR_X86_SSE2_PSLL_W           = 445
INTR_X86_SSE2_PSLLI_D          = 446
INTR_X86_SSE2_PSLLI_Q          = 447
INTR_X86_SSE2_PSLLI_W          = 448
INTR_X86_SSE2_PSRA_D           = 449
INTR_X86_SSE2_PSRA_W           = 450
INTR_X86_SSE2_PSRAI_D          = 451
INTR_X86_SSE2_PSRAI_W          = 452
INTR_X86_SSE2_PSRL_D           = 453
INTR_X86_SSE2_PSRL_DQ          = 454
INTR_X86_SSE2_PSRL_DQ_BS       = 455
INTR_X86_SSE2_PSRL_Q           = 456
INTR_X86_SSE2_PSRL_W           = 457
INTR_X86_SSE2_PSRLI_D          = 458
INTR_X86_SSE2_PSRLI_Q          = 459
INTR_X86_SSE2_PSRLI_W          = 460
INTR_X86_SSE2_PSUBS_B          = 461
INTR_X86_SSE2_PSUBS_W          = 462
INTR_X86_SSE2_PSUBUS_B         = 463
INTR_X86_SSE2_PSUBUS_W         = 464
INTR_X86_SSE2_SQRT_PD          = 465
INTR_X86_SSE2_SQRT_SD          = 466
INTR_X86_SSE2_STOREL_DQ        = 467
INTR_X86_SSE2_STOREU_DQ        = 468
INTR_X86_SSE2_STOREU_PD        = 469
INTR_X86_SSE2_SUB_SD           = 470
INTR_X86_SSE2_UCOMIEQ_SD       = 471
INTR_X86_SSE2_UCOMIGE_SD       = 472
INTR_X86_SSE2_UCOMIGT_SD       = 473
INTR_X86_SSE2_UCOMILE_SD       = 474
INTR_X86_SSE2_UCOMILT_SD       = 475
INTR_X86_SSE2_UCOMINEQ_SD      = 476
INTR_X86_SSE3_ADDSUB_PD        = 477
INTR_X86_SSE3_ADDSUB_PS        = 478
INTR_X86_SSE3_HADD_PD          = 479
INTR_X86_SSE3_HADD_PS          = 480
INTR_X86_SSE3_HSUB_PD          = 481
INTR_X86_SSE3_HSUB_PS          = 482
INTR_X86_SSE3_LDU_DQ           = 483
INTR_X86_SSE3_MONITOR          = 484
INTR_X86_SSE3_MWAIT            = 485
INTR_X86_SSE41_BLENDPD         = 486
INTR_X86_SSE41_BLENDPS         = 487
INTR_X86_SSE41_BLENDVPD        = 488
INTR_X86_SSE41_BLENDVPS        = 489
INTR_X86_SSE41_DPPD            = 490
INTR_X86_SSE41_DPPS            = 491
INTR_X86_SSE41_EXTRACTPS       = 492
INTR_X86_SSE41_INSERTPS        = 493
INTR_X86_SSE41_MOVNTDQA        = 494
INTR_X86_SSE41_MPSADBW         = 495
INTR_X86_SSE41_PACKUSDW        = 496
INTR_X86_SSE41_PBLENDVB        = 497
INTR_X86_SSE41_PBLENDW         = 498
INTR_X86_SSE41_PCMPEQQ         = 499
INTR_X86_SSE41_PEXTRB          = 500
INTR_X86_SSE41_PEXTRD          = 501
INTR_X86_SSE41_PEXTRQ          = 502
INTR_X86_SSE41_PHMINPOSUW      = 503
INTR_X86_SSE41_PINSRB          = 504
INTR_X86_SSE41_PMAXSB          = 505
INTR_X86_SSE41_PMAXSD          = 506
INTR_X86_SSE41_PMAXUD          = 507
INTR_X86_SSE41_PMAXUW          = 508
INTR_X86_SSE41_PMINSB          = 509
INTR_X86_SSE41_PMINSD          = 510
INTR_X86_SSE41_PMINUD          = 511
INTR_X86_SSE41_PMINUW          = 512
INTR_X86_SSE41_PMOVSXBD        = 513
INTR_X86_SSE41_PMOVSXBQ        = 514
INTR_X86_SSE41_PMOVSXBW        = 515
INTR_X86_SSE41_PMOVSXDQ        = 516
INTR_X86_SSE41_PMOVSXWD        = 517
INTR_X86_SSE41_PMOVSXWQ        = 518
INTR_X86_SSE41_PMOVZXBD        = 519
INTR_X86_SSE41_PMOVZXBQ        = 520
INTR_X86_SSE41_PMOVZXBW        = 521
INTR_X86_SSE41_PMOVZXDQ        = 522
INTR_X86_SSE41_PMOVZXWD        = 523
INTR_X86_SSE41_PMOVZXWQ        = 524
INTR_X86_SSE41_PMULDQ          = 525
INTR_X86_SSE41_PMULLD          = 526
INTR_X86_SSE41_ROUND_PD        = 527
INTR_X86_SSE41_ROUND_PS        = 528
INTR_X86_SSE41_ROUND_SD        = 529
INTR_X86_SSE41_ROUND_SS        = 530
INTR_X86_SSE42_PCMPGTQ         = 531
INTR_X86_SSE_ADD_SS            = 532
INTR_X86_SSE_CMP_PS            = 533
INTR_X86_SSE_CMP_SS            = 534
INTR_X86_SSE_COMIEQ_SS         = 535
INTR_X86_SSE_COMIGE_SS         = 536
INTR_X86_SSE_COMIGT_SS         = 537
INTR_X86_SSE_COMILE_SS         = 538
INTR_X86_SSE_COMILT_SS         = 539
INTR_X86_SSE_COMINEQ_SS        = 540
INTR_X86_SSE_CVTPD2PI          = 541
INTR_X86_SSE_CVTPI2PD          = 542
INTR_X86_SSE_CVTPI2PS          = 543
INTR_X86_SSE_CVTPS2PI          = 544
INTR_X86_SSE_CVTSI2SS          = 545
INTR_X86_SSE_CVTSI642SS        = 546
INTR_X86_SSE_CVTSS2SI          = 547
INTR_X86_SSE_CVTSS2SI64        = 548
INTR_X86_SSE_CVTTPD2PI         = 549
INTR_X86_SSE_CVTTPS2PI         = 550
INTR_X86_SSE_CVTTSS2SI         = 551
INTR_X86_SSE_CVTTSS2SI64       = 552
INTR_X86_SSE_DIV_SS            = 553
INTR_X86_SSE_LDMXCSR           = 554
INTR_X86_SSE_LOADU_PS          = 555
INTR_X86_SSE_MAX_PS            = 556
INTR_X86_SSE_MAX_SS            = 557
INTR_X86_SSE_MIN_PS            = 558
INTR_X86_SSE_MIN_SS            = 559
INTR_X86_SSE_MOVMSK_PS         = 560
INTR_X86_SSE_MOVNT_PS          = 561
INTR_X86_SSE_MUL_SS            = 562
INTR_X86_SSE_RCP_PS            = 563
INTR_X86_SSE_RCP_SS            = 564
INTR_X86_SSE_RSQRT_PS          = 565
INTR_X86_SSE_RSQRT_SS          = 566
INTR_X86_SSE_SFENCE            = 567
INTR_X86_SSE_SQRT_PS           = 568
INTR_X86_SSE_SQRT_SS           = 569
INTR_X86_SSE_STMXCSR           = 570
INTR_X86_SSE_STOREU_PS         = 571
INTR_X86_SSE_SUB_SS            = 572
INTR_X86_SSE_UCOMIEQ_SS        = 573
INTR_X86_SSE_UCOMIGE_SS        = 574
INTR_X86_SSE_UCOMIGT_SS        = 575
INTR_X86_SSE_UCOMILE_SS        = 576
INTR_X86_SSE_UCOMILT_SS        = 577
INTR_X86_SSE_UCOMINEQ_SS       = 578
INTR_X86_SSSE3_PABS_B          = 579
INTR_X86_SSSE3_PABS_B_128      = 580
INTR_X86_SSSE3_PABS_D          = 581
INTR_X86_SSSE3_PABS_D_128      = 582
INTR_X86_SSSE3_PABS_W          = 583
INTR_X86_SSSE3_PABS_W_128      = 584
INTR_X86_SSSE3_PALIGN_R        = 585
INTR_X86_SSSE3_PALIGN_R_128    = 586
INTR_X86_SSSE3_PHADD_D         = 587
INTR_X86_SSSE3_PHADD_D_128     = 588
INTR_X86_SSSE3_PHADD_SW        = 589
INTR_X86_SSSE3_PHADD_SW_128    = 590
INTR_X86_SSSE3_PHADD_W         = 591
INTR_X86_SSSE3_PHADD_W_128     = 592
INTR_X86_SSSE3_PHSUB_D         = 593
INTR_X86_SSSE3_PHSUB_D_128     = 594
INTR_X86_SSSE3_PHSUB_SW        = 595
INTR_X86_SSSE3_PHSUB_SW_128    = 596
INTR_X86_SSSE3_PHSUB_W         = 597
INTR_X86_SSSE3_PHSUB_W_128     = 598
INTR_X86_SSSE3_PMADD_UB_SW     = 599
INTR_X86_SSSE3_PMADD_UB_SW_128 = 600
INTR_X86_SSSE3_PMUL_HR_SW      = 601
INTR_X86_SSSE3_PMUL_HR_SW_128  = 602
INTR_X86_SSSE3_PSHUF_B         = 603
INTR_X86_SSSE3_PSHUF_B_128     = 604
INTR_X86_SSSE3_PSIGN_B         = 605
INTR_X86_SSSE3_PSIGN_B_128     = 606
INTR_X86_SSSE3_PSIGN_D         = 607
INTR_X86_SSSE3_PSIGN_D_128     = 608
INTR_X86_SSSE3_PSIGN_W         = 609
INTR_X86_SSSE3_PSIGN_W_128     = 610
INTR_XCORE_BITREV              = 611
INTR_XCORE_GETID               = 612


#===----------------------------------------------------------------------===
# Helpers (for internal use)
#===----------------------------------------------------------------------===

def check_is_type(obj):     check_gen(obj, Type)
def check_is_value(obj):    check_gen(obj, Value)
def check_is_constant(obj): check_gen(obj, Constant)
def check_is_function(obj): check_gen(obj, Function)
def check_is_basic_block(obj): check_gen(obj, BasicBlock)
def check_is_module(obj):   check_gen(obj, Module)
def check_is_module_provider(obj): check_gen(obj, ModuleProvider)

def unpack_types(objlist):     return unpack_gen(objlist, check_is_type)
def unpack_values(objlist):    return unpack_gen(objlist, check_is_value)
def unpack_constants(objlist): return unpack_gen(objlist, check_is_constant)

def check_is_callable(obj):
    if isinstance(obj, Function):
        return
    type = obj.type
    if isinstance(type, PointerType) and \
        isinstance(type.pointee, FunctionType):
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

class Module(llvm.Ownable):
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

    __metaclass__ = ObjectCache

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
        invoked, and will behave in undefined ways.
        """
        check_is_module(other)
        ret = _core.LLVMLinkModules(self.ptr, other.ptr)
        if isinstance(ret, str):
            raise llvm.LLVMException, ret

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
        return wrapiter(_core.LLVMGetFirstGlobal, _core.LLVMGetNextGlobal,
            self.ptr, _make_value)

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
        """All functions in this module.

        This property returns a generator that yields Function objects.
        Use it like this:
          for f in module_obj.functions:
            # f is an instance of Function
            # do stuff with f
        """
        return wrapiter(_core.LLVMGetFirstFunction, 
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

        This object is no longer valid after refining, so do not hold references
        to it after calling. See the user guide for examples on how to use this."""

        check_is_type(dest)
        _core.LLVMRefineType(self.ptr, dest.ptr)
        self.ptr = None


class IntegerType(Type):
    """Represents an integer type."""

    def __init__(self, ptr, kind):
        """DO NOT CALL DIRECTLY.

        Use one of the static methods of the *base* class (Type) instead."""
        Type.__init__(self, ptr, kind)

    @property
    def width(self):
        """The width of the integer type, in bits."""
        return _core.LLVMGetIntTypeWidth(self.ptr)


class FunctionType(Type):
    """Represents a function type."""

    def __init__(self, ptr, kind):
        """DO NOT CALL DIRECTLY.

        Use one of the static methods of the *base* class (Type) instead."""
        Type.__init__(self, ptr, kind)

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

    def __init__(self, ptr, kind):
        """DO NOT CALL DIRECTLY.

        Use one of the static methods of the *base* class (Type) instead."""
        Type.__init__(self, ptr, kind)

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

    def __init__(self, ptr, kind):
        """DO NOT CALL DIRECTLY.

        Use one of the static methods of the *base* class (Type) instead."""
        Type.__init__(self, ptr, kind)

    @property
    def element(self):
        ptr  = _core.LLVMGetElementType(self.ptr)
        kind = _core.LLVMGetTypeKind(ptr)
        return _make_type(ptr, kind)

    @property
    def count(self):
        return _core.LLVMGetArrayLength(self.ptr)


class PointerType(Type):

    def __init__(self, ptr, kind):
        """DO NOT CALL DIRECTLY.

        Use one of the static methods of the *base* class (Type) instead."""
        Type.__init__(self, ptr, kind)

    @property
    def pointee(self):
        ptr = _core.LLVMGetElementType(self.ptr)
        kind = _core.LLVMGetTypeKind(ptr)
        return _make_type(ptr, kind)

    @property
    def address_space(self):
        return _core.LLVMGetPointerAddressSpace(self.ptr)


class VectorType(Type):

    def __init__(self, ptr, kind):
        """DO NOT CALL DIRECTLY.

        Use one of the static methods of the *base* class (Type) instead."""
        Type.__init__(self, ptr, kind)

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

class Value(object):

    __metaclass__ = ObjectCache

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
        return _core.LLVMValueGetID(ptr)

    @property
    def type(self):
        ptr  = _core.LLVMTypeOf(self.ptr)
        kind = _core.LLVMGetTypeKind(ptr)
        return _make_type(ptr, kind)


class Constant(Value):

    @staticmethod
    def null(ty):
        check_is_type(ty)
        return _make_value(_core.LLVMConstNull(ty.ptr));
        
    @staticmethod
    def all_ones(ty):
        check_is_type(ty)
        return _make_value(_core.LLVMConstAllOnes(ty.ptr));
        
    @staticmethod
    def undef(ty):
        check_is_type(ty)
        return _make_value(_core.LLVMGetUndef(ty.ptr));

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

    def __init__(self, ptr):
        Value.__init__(self, ptr)
        
    def neg(self):
        return _make_value(_core.LLVMConstNeg(self.ptr))
        
    def not_(self):
        return _make_value(_core.LLVMConstNot(self.ptr))
        
    def add(self, rhs):
        check_is_constant(rhs)
        return _make_value(_core.LLVMConstAdd(self.ptr, rhs.ptr))

    def sub(self, rhs):
        check_is_constant(rhs)
        return _make_value(_core.LLVMConstSub(self.ptr, rhs.ptr))

    def mul(self, rhs):
        check_is_constant(rhs)
        return _make_value(_core.LLVMConstMul(self.ptr, rhs.ptr))

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

    def vicmp(self, int_pred, rhs):
        check_is_constant(rhs)
        return _make_value(_core.LLVMConstVICmp(int_pred, self.ptr, rhs.ptr))

    def vfcmp(self, real_pred, rhs):
        check_is_constant(rhs)
        return _make_value(_core.LLVMConstVFCmp(real_pred, self.ptr, rhs.ptr))

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
        return _make_value(_core.LLVMConstSelect(self.ptr, true_const.ptr, false_const.ptr))

    def extract_element(self, index): # note: self must be a _vector_ constant
        check_is_constant(index)
        return _make_value(_core.LLVMConstExtractElement(self.ptr, index.ptr))

    def insert_element(self, value, index): # note: self must be a _vector_ constant
        check_is_constant(value)
        check_is_constant(index)
        return _make_value(_core.LLVMConstInsertElement(self.ptr, value.ptr, index.ptr))

    def shuffle_vector(self, vector_b, mask): # note: self must be a _vector_ constant
        check_is_constant(vector_b)   # note: vector_b must be a _vector_ constant
        check_is_constant(mask)
        return _make_value(_core.LLVMConstShuffleVector(self.ptr, vector_b.ptr, mask.ptr))


class ConstantExpr(Constant):

    def __init__(self, ptr):
        Constant.__init__(self, ptr)


class ConstantAggregateZero(Constant):

    def __init__(self, ptr):
        Constant.__init__(self, ptr)


class ConstantInt(Constant):

    def __init__(self, ptr):
        Constant.__init__(self, ptr)


class ConstantFP(Constant):

    def __init__(self, ptr):
        Constant.__init__(self, ptr)


class ConstantArray(Constant):

    def __init__(self, ptr):
        Constant.__init__(self, ptr)


class ConstantStruct(Constant):

    def __init__(self, ptr):
        Constant.__init__(self, ptr)


class ConstantVector(Constant):

    def __init__(self, ptr):
        Constant.__init__(self, ptr)


class ConstantPointerNull(Constant):

    def __init__(self, ptr):
        Constant.__init__(self, ptr)


class GlobalValue(Constant):

    def __init__(self, ptr):
        Constant.__init__(self, ptr)
        # Hang on to the module, don't let it die before we do.
        # It is nice to have just a map of functions without 
        # retaining a ref to the owning module.
        self._module_obj = self.module

    def _get_linkage(self): return _core.LLVMGetLinkage(self.ptr)
    def _set_linkage(self, value): _core.LLVMSetLinkage(self.ptr, value)
    linkage = property(_get_linkage, _set_linkage)

    def _get_section(self): return _core.LLVMGetSection(self.ptr)
    def _set_section(self, value): return _core.LLVMSetSection(self.ptr, value)
    section = property(_get_section, _set_section)
    
    def _get_visibility(self): return _core.LLVMGetVisibility(self.ptr)
    def _set_visibility(self, value): return _core.LLVMSetVisibility(self.ptr, value)
    visibility = property(_get_visibility, _set_visibility)

    def _get_alignment(self): return _core.LLVMGetAlignment(self.ptr)
    def _set_alignment(self, value): return _core.LLVMSetAlignment(self.ptr, value)
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

    def __init__(self, ptr):
        GlobalValue.__init__(self, ptr)

    def delete(self):
        _core.LLVMDeleteGlobal(self.ptr)

    def _get_initializer(self):
        if _core.LLVMHasInitializer(self.ptr):
            return Constant(_core.LLVMGetInitializer(self.ptr))
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

    global_constant = property(_get_is_global_constant, _set_is_global_constant)


class Argument(Value):

    def __init__(self, ptr):
        Value.__init__(self, ptr)

    def add_attribute(self, attr):
        _core.LLVMAddAttribute(self.ptr, attr)

    def remove_attribute(self, attr):
        _core.LLVMRemoveAttribute(self.ptr, attr)

    def set_alignment(self, align):
        _core.LLVMSetParamAlignment(self.ptr, align)


class Function(GlobalValue):

    @staticmethod
    def new(module, func_ty, name):
        check_is_module(module)
        check_is_type(func_ty)
        return _make_value(_core.LLVMAddFunction(module.ptr, name, \
            func_ty.ptr))

    @staticmethod
    def get_or_insert(module, func_ty, name):
        check_is_module(module)
        check_is_type(func_ty)
        return _make_value(_core.LLVMModuleGetOrInsertFunction(module.ptr, \
            name, func_ty.ptr))

    @staticmethod
    def get(module, name):
        check_is_module(module)
        ptr = _core.LLVMGetNamedFunction(module.ptr, name)
        if not ptr:
            raise llvm.LLVMException, ("no function named `%s`" % name)
        return _make_value(ptr)
    
    @staticmethod
    def intrinsic(module, id, types):
        check_is_module(module)
        ptrs = unpack_types(types)
        return _make_value(_core.LLVMGetIntrinsic(module.ptr, id, ptrs))

    def __init__(self, ptr):
        GlobalValue.__init__(self, ptr)

    def delete(self):
        _core.LLVMDeleteFunction(self.ptr)

    @property
    def intrinsic_id(self):
        return _core.LLVMGetIntrinsicID(self.ptr)

    def _get_cc(self): return _core.LLVMGetFunctionCallConv(self.ptr)
    def _set_cc(self, value): _core.LLVMSetFunctionCallConv(self.ptr, value)
    calling_convention = property(_get_cc, _set_cc)

    def _get_coll(self): return _core.LLVMGetGC(self.ptr)
    def _set_coll(self, value): _core.LLVMSetGC(self.ptr, value)
    collector = property(_get_coll, _set_coll)

    @property
    def args(self):
        return wrapiter(_core.LLVMGetFirstParam, _core.LLVMGetNextParam,
            self.ptr, _make_value)

    @property
    def basic_block_count(self):
        return _core.LLVMCountBasicBlocks(self.ptr)

    def get_entry_basic_block(self):
        if self.basic_block_count == 0:
            return None
        return _make_value(_core.LLVMGetEntryBasicBlock(self.ptr))

    def append_basic_block(self, name):
        return _make_value(_core.LLVMAppendBasicBlock(self.ptr, name))

    @property
    def basic_blocks(self):
        return wrapiter(_core.LLVMGetFirstBasicBlock, 
            _core.LLVMGetNextBasicBlock, self.ptr, _make_value)

    def viewCFG(self):
        return _core.LLVMViewFunctionCFG(self.ptr)

    def viewCFGOnly(self):
        return _core.LLVMViewFunctionCFGOnly(self.ptr)

    def verify(self):
        # Although we're just asking LLVM to return the success or
        # failure, it appears to print result to stderr and abort.
        return _core.LLVMVerifyFunction(self.ptr) != 0


#===----------------------------------------------------------------------===
# Instruction
#===----------------------------------------------------------------------===

class Instruction(Value):

    def __init__(self, ptr):
        Value.__init__(self, ptr)

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
    def is_trapping(self):
        return _core.LLVMInstIsTrapping(self.ptr) != 0

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

    @property
    def operand_count(self):
        return _core.LLVMInstGetNumOperands(self.ptr)

    @property
    def operands(self):
        """Yields operands of this instruction."""
        return [self._get_operand(i) for i in range(self.operand_count)]

    def _get_operand(self, i):
        return _make_value(_core.LLVMInstGetOperand(self.ptr, i))


class CallOrInvokeInstruction(Instruction):

    def __init__(self, ptr):
        Instruction.__init__(self, ptr)

    def _get_cc(self): return _core.LLVMGetInstructionCallConv(self.ptr)
    def _set_cc(self, value): _core.LLVMSetInstructionCallConv(self.ptr, value)
    calling_convention = property(_get_cc, _set_cc)

    def add_parameter_attribute(self, idx, attr):
        _core.LLVMAddInstrAttribute(self.ptr, idx, attr)

    def remove_parameter_attribute(self, idx, attr):
        _core.LLVMRemoveInstrAttribute(self.ptr, idx, attr)

    def set_parameter_alignment(self, idx, align):
        _core.LLVMSetInstrParamAlignment(self.ptr, idx, align)


class PHINode(Instruction):

    def __init__(self, ptr):
        Instruction.__init__(self, ptr)

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

    def __init__(self, ptr):
        Instruction.__init__(self, ptr)

    def add_case(self, const, bblk):
        check_is_constant(const) # and has to be an int too
        check_is_basic_block(bblk)
        _core.LLVMAddCase(self.ptr, const.ptr, bblk.ptr)


#===----------------------------------------------------------------------===
# Basic block
#===----------------------------------------------------------------------===

class BasicBlock(Value):

    def __init__(self, ptr):
        self.ptr = ptr

    def insert_before(self, name):
        return _make_value(_core.LLVMInsertBasicBlock(self.ptr, name))

    def delete(self):
        _core.LLVMDeleteBasicBlock(self.ptr)
        self.ptr = None

    @property
    def function(self):
        func_ptr = _core.LLVMGetBasicBlockParent(self.ptr)
        return _make_value(func_ptr)

    @property
    def instructions(self):
        return wrapiter(_core.LLVMGetFirstInstruction,
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
    VALUE_CONSTANT_EXPR                   : ConstantExpr,
    VALUE_INLINE_ASM                      : Constant,
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
}

def _make_value(ptr):
    kind = _core.LLVMValueGetID(ptr)
    # based on kind, create one of the Value subclasses
    if kind in __class_for_valueid:
        return __class_for_valueid[kind](ptr)
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
        # Avoids using "blk.instructions", which will fetch all the
        # instructions into a list. Don't try this at home, though.
        inst_ptr = _core.LLVMGetFirstInstruction(self.block.ptr)
        if inst_ptr:
            # Issue #10: inst_ptr can be None if b/b has no insts.
            inst = Instruction(inst_ptr)
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
        return _make_value(_core.LLVMBuildCondBr(self.ptr, if_value.ptr, then_blk.ptr, else_blk.ptr))
        
    def switch(self, value, else_blk, n=10):
        check_is_value(value)  # value has to be of any 'int' type
        check_is_basic_block(else_blk)
        return _make_value(_core.LLVMBuildSwitch(self.ptr, value.ptr, else_blk.ptr, n))
        
    def invoke(self, func, args, then_blk, catch_blk, name=""):
        check_is_callable(func)
        check_is_basic_block(then_blk)
        check_is_basic_block(catch_blk)
        args2 = unpack_values(args)
        return _make_value(_core.LLVMBuildInvoke(self.ptr, func.ptr, args2, then_blk.ptr, catch_blk.ptr, name))

    def unwind(self):
        return _make_value(_core.LLVMBuildUnwind(self.ptr))
        
    def unreachable(self):
        return _make_value(_core.LLVMBuildUnreachable(self.ptr))

    # arithmethic, bitwise and logical
    
    def add(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return _make_value(_core.LLVMBuildAdd(self.ptr, lhs.ptr, rhs.ptr, name))
        
    def sub(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return _make_value(_core.LLVMBuildSub(self.ptr, lhs.ptr, rhs.ptr, name))

    def mul(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return _make_value(_core.LLVMBuildMul(self.ptr, lhs.ptr, rhs.ptr, name))

    def udiv(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return _make_value(_core.LLVMBuildUDiv(self.ptr, lhs.ptr, rhs.ptr, name))

    def sdiv(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return _make_value(_core.LLVMBuildSDiv(self.ptr, lhs.ptr, rhs.ptr, name))

    def fdiv(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return _make_value(_core.LLVMBuildFDiv(self.ptr, lhs.ptr, rhs.ptr, name))

    def urem(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return _make_value(_core.LLVMBuildURem(self.ptr, lhs.ptr, rhs.ptr, name))

    def srem(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return _make_value(_core.LLVMBuildSRem(self.ptr, lhs.ptr, rhs.ptr, name))

    def frem(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return _make_value(_core.LLVMBuildFRem(self.ptr, lhs.ptr, rhs.ptr, name))

    def shl(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return _make_value(_core.LLVMBuildShl(self.ptr, lhs.ptr, rhs.ptr, name))

    def lshr(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return _make_value(_core.LLVMBuildLShr(self.ptr, lhs.ptr, rhs.ptr, name))

    def ashr(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return _make_value(_core.LLVMBuildAShr(self.ptr, lhs.ptr, rhs.ptr, name))

    def and_(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return _make_value(_core.LLVMBuildAnd(self.ptr, lhs.ptr, rhs.ptr, name))

    def or_(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return _make_value(_core.LLVMBuildOr(self.ptr, lhs.ptr, rhs.ptr, name))

    def xor(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return _make_value(_core.LLVMBuildXor(self.ptr, lhs.ptr, rhs.ptr, name))

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
        return _make_value(_core.LLVMBuildArrayMalloc(self.ptr, ty.ptr, size.ptr, name))

    def alloca(self, ty, name=""):
        check_is_type(ty)
        return _make_value(_core.LLVMBuildAlloca(self.ptr, ty.ptr, name))

    def alloca_array(self, ty, size, name=""):
        check_is_type(ty)
        check_is_value(size)
        return _make_value(_core.LLVMBuildArrayAlloca(self.ptr, ty.ptr, size.ptr, name))

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
        return _make_value(_core.LLVMBuildGEP(self.ptr, ptr.ptr, index_ptrs, name))

    # casts and extensions

    def trunc(self, value, dest_ty, name=""):
        check_is_value(value)
        check_is_type(dest_ty)
        return _make_value(_core.LLVMBuildTrunc(self.ptr, value.ptr, dest_ty.ptr, name))

    def zext(self, value, dest_ty, name=""):
        check_is_value(value)
        check_is_type(dest_ty)
        return _make_value(_core.LLVMBuildZExt(self.ptr, value.ptr, dest_ty.ptr, name))

    def sext(self, value, dest_ty, name=""):
        check_is_value(value)
        check_is_type(dest_ty)
        return _make_value(_core.LLVMBuildSExt(self.ptr, value.ptr, dest_ty.ptr, name))

    def fptoui(self, value, dest_ty, name=""):
        check_is_value(value)
        check_is_type(dest_ty)
        return _make_value(_core.LLVMBuildFPToUI(self.ptr, value.ptr, dest_ty.ptr, name))

    def fptosi(self, value, dest_ty, name=""):
        check_is_value(value)
        check_is_type(dest_ty)
        return _make_value(_core.LLVMBuildFPToSI(self.ptr, value.ptr, dest_ty.ptr, name))

    def uitofp(self, value, dest_ty, name=""):
        check_is_value(value)
        check_is_type(dest_ty)
        return _make_value(_core.LLVMBuildUIToFP(self.ptr, value.ptr, dest_ty.ptr, name))

    def sitofp(self, value, dest_ty, name=""):
        check_is_value(value)
        check_is_type(dest_ty)
        return _make_value(_core.LLVMBuildSIToFP(self.ptr, value.ptr, dest_ty.ptr, name))

    def fptrunc(self, value, dest_ty, name=""):
        check_is_value(value)
        check_is_type(dest_ty)
        return _make_value(_core.LLVMBuildFPTrunc(self.ptr, value.ptr, dest_ty.ptr, name))

    def fpext(self, value, dest_ty, name=""):
        check_is_value(value)
        check_is_type(dest_ty)
        return _make_value(_core.LLVMBuildFPExt(self.ptr, value.ptr, dest_ty.ptr, name))

    def ptrtoint(self, value, dest_ty, name=""):
        check_is_value(value)
        check_is_type(dest_ty)
        return _make_value(_core.LLVMBuildPtrToInt(self.ptr, value.ptr, dest_ty.ptr, name))

    def inttoptr(self, value, dest_ty, name=""):
        check_is_value(value)
        check_is_type(dest_ty)
        return _make_value(_core.LLVMBuildIntToPtr(self.ptr, value.ptr, dest_ty.ptr, name))

    def bitcast(self, value, dest_ty, name=""):
        check_is_value(value)
        check_is_type(dest_ty)
        return _make_value(_core.LLVMBuildBitCast(self.ptr, value.ptr, dest_ty.ptr, name))

    # comparisons

    def icmp(self, ipred, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return _make_value(_core.LLVMBuildICmp(self.ptr, ipred, lhs.ptr, rhs.ptr, name))
        
    def fcmp(self, rpred, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return _make_value(_core.LLVMBuildFCmp(self.ptr, rpred, lhs.ptr, rhs.ptr, name))

    def vicmp(self, ipred, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return _make_value(_core.LLVMBuildVICmp(self.ptr, ipred, lhs.ptr, rhs.ptr, name))
        
    def vfcmp(self, rpred, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return _make_value(_core.LLVMBuildVFCmp(self.ptr, rpred, lhs.ptr, rhs.ptr, name))

    # misc

    def getresult(self, retval, idx, name=""):
        check_is_value(retval)
        return _make_value(_core.LLVMBuildGetResult(self.ptr, retval.ptr, idx, name))

    def phi(self, ty, name=""):
        check_is_type(ty)
        return _make_value(_core.LLVMBuildPhi(self.ptr, ty.ptr, name))
        
    def call(self, fn, args, name=""):
        check_is_callable(fn)
        arg_ptrs = unpack_values(args)
        return _make_value(_core.LLVMBuildCall(self.ptr, fn.ptr, arg_ptrs, name))
        
    def select(self, cond, then_value, else_value, name=""):
        check_is_value(cond)
        check_is_value(then_value)
        check_is_value(else_value)
        return _make_value(_core.LLVMBuildSelect(self.ptr, cond.ptr, then_value.ptr, else_value.ptr, name))
    
    def vaarg(self, list_val, ty, name=""):
        check_is_value(list_val)
        check_is_type(ty)
        return _make_value(_core.LLVMBuildVAArg(self.ptr, list_val.ptr, ty.ptr, name))
    
    def extract_element(self, vec_val, idx_val, name=""):
        check_is_value(vec_val)
        check_is_value(idx_val)
        return _make_value(_core.LLVMBuildExtractElement(self.ptr, vec_val.ptr, idx_val.ptr, name))
    
    def insert_element(self, vec_val, elt_val, idx_val, name=""):
        check_is_value(vec_val)
        check_is_value(elt_val)
        check_is_value(idx_val)
        return _make_value(_core.LLVMBuildInsertElement(self.ptr, vec_val.ptr, elt_val.ptr, idx_val.ptr, name))

    def shuffle_vector(self, vecA, vecB, mask, name=""):
        check_is_value(vecA)
        check_is_value(vecB)
        check_is_value(mask)
        return _make_value(_core.LLVMBuildShuffleVector(self.ptr, vecA.ptr, vecB.ptr, mask.ptr, name))


#===----------------------------------------------------------------------===
# Module provider
#===----------------------------------------------------------------------===

class ModuleProvider(llvm.Ownable):

    @staticmethod
    def new(module):
        check_is_module(module)
        check_is_unowned(module)
        return ModuleProvider(
            _core.LLVMCreateModuleProviderForExistingModule(module.ptr),
            module)

    def __init__(self, ptr, module):
        llvm.Ownable.__init__(self, ptr, _core.LLVMDisposeModuleProvider)
        module._own(self)
        # a module provider is both a owner (of modules) and an ownable
        # (can be owned by execution engines)


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

