"""Core classes of LLVM.

The llvm.core module contains classes and constants required to build the
in-memory intermediate representation (IR) data structures."""


import llvm                 # top-level, for common stuff
import llvm._core as _core  # C wrappers
from llvm._util import *    # utility functions


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

# intrinsic IDs
INTR_ANNOTATION                = 1
INTR_ARM_THREAD_POINTER        = 2
INTR_ATOMIC_LAS                = 3
INTR_ATOMIC_LCS                = 4
INTR_ATOMIC_LOAD_AND           = 5
INTR_ATOMIC_LOAD_MAX           = 6
INTR_ATOMIC_LOAD_MIN           = 7
INTR_ATOMIC_LOAD_OR            = 8
INTR_ATOMIC_LOAD_UMAX          = 9
INTR_ATOMIC_LOAD_UMIN          = 10
INTR_ATOMIC_LOAD_XOR           = 11
INTR_ATOMIC_LSS                = 12
INTR_ATOMIC_SWAP               = 13
INTR_BSWAP                     = 14
INTR_COS                       = 15
INTR_CTLZ                      = 16
INTR_CTPOP                     = 17
INTR_CTTZ                      = 18
INTR_DBG_DECLARE               = 19
INTR_DBG_FUNC_START            = 20
INTR_DBG_REGION_END            = 21
INTR_DBG_REGION_START          = 22
INTR_DBG_STOPPOINT             = 23
INTR_EH_DWARF_CFA              = 24
INTR_EH_EXCEPTION              = 25
INTR_EH_RETURN                 = 26
INTR_EH_SELECTOR_I32           = 27
INTR_EH_SELECTOR_I64           = 28
INTR_EH_TYPEID_FOR_I32         = 29
INTR_EH_TYPEID_FOR_I64         = 30
INTR_EH_UNWIND_INIT            = 31
INTR_FLT_ROUNDS                = 32
INTR_FRAMEADDRESS              = 33
INTR_GCREAD                    = 34
INTR_GCROOT                    = 35
INTR_GCWRITE                   = 36
INTR_INIT_TRAMPOLINE           = 37
INTR_LONGJMP                   = 38
INTR_MEMCPY_I32                = 39
INTR_MEMCPY_I64                = 40
INTR_MEMMOVE_I32               = 41
INTR_MEMMOVE_I64               = 42
INTR_MEMORY_BARRIER            = 43
INTR_MEMSET_I32                = 44
INTR_MEMSET_I64                = 45
INTR_PART_SELECT               = 46
INTR_PART_SET                  = 47
INTR_PCMARKER                  = 48
INTR_POW                       = 49
INTR_POWI                      = 50
INTR_PPC_ALTIVEC_DSS           = 51
INTR_PPC_ALTIVEC_DSSALL        = 52
INTR_PPC_ALTIVEC_DST           = 53
INTR_PPC_ALTIVEC_DSTST         = 54
INTR_PPC_ALTIVEC_DSTSTT        = 55
INTR_PPC_ALTIVEC_DSTT          = 56
INTR_PPC_ALTIVEC_LVEBX         = 57
INTR_PPC_ALTIVEC_LVEHX         = 58
INTR_PPC_ALTIVEC_LVEWX         = 59
INTR_PPC_ALTIVEC_LVSL          = 60
INTR_PPC_ALTIVEC_LVSR          = 61
INTR_PPC_ALTIVEC_LVX           = 62
INTR_PPC_ALTIVEC_LVXL          = 63
INTR_PPC_ALTIVEC_MFVSCR        = 64
INTR_PPC_ALTIVEC_MTVSCR        = 65
INTR_PPC_ALTIVEC_STVEBX        = 66
INTR_PPC_ALTIVEC_STVEHX        = 67
INTR_PPC_ALTIVEC_STVEWX        = 68
INTR_PPC_ALTIVEC_STVX          = 69
INTR_PPC_ALTIVEC_STVXL         = 70
INTR_PPC_ALTIVEC_VADDCUW       = 71
INTR_PPC_ALTIVEC_VADDSBS       = 72
INTR_PPC_ALTIVEC_VADDSHS       = 73
INTR_PPC_ALTIVEC_VADDSWS       = 74
INTR_PPC_ALTIVEC_VADDUBS       = 75
INTR_PPC_ALTIVEC_VADDUHS       = 76
INTR_PPC_ALTIVEC_VADDUWS       = 77
INTR_PPC_ALTIVEC_VAVGSB        = 78
INTR_PPC_ALTIVEC_VAVGSH        = 79
INTR_PPC_ALTIVEC_VAVGSW        = 80
INTR_PPC_ALTIVEC_VAVGUB        = 81
INTR_PPC_ALTIVEC_VAVGUH        = 82
INTR_PPC_ALTIVEC_VAVGUW        = 83
INTR_PPC_ALTIVEC_VCFSX         = 84
INTR_PPC_ALTIVEC_VCFUX         = 85
INTR_PPC_ALTIVEC_VCMPBFP       = 86
INTR_PPC_ALTIVEC_VCMPBFP_P     = 87
INTR_PPC_ALTIVEC_VCMPEQFP      = 88
INTR_PPC_ALTIVEC_VCMPEQFP_P    = 89
INTR_PPC_ALTIVEC_VCMPEQUB      = 90
INTR_PPC_ALTIVEC_VCMPEQUB_P    = 91
INTR_PPC_ALTIVEC_VCMPEQUH      = 92
INTR_PPC_ALTIVEC_VCMPEQUH_P    = 93
INTR_PPC_ALTIVEC_VCMPEQUW      = 94
INTR_PPC_ALTIVEC_VCMPEQUW_P    = 95
INTR_PPC_ALTIVEC_VCMPGEFP      = 96
INTR_PPC_ALTIVEC_VCMPGEFP_P    = 97
INTR_PPC_ALTIVEC_VCMPGTFP      = 98
INTR_PPC_ALTIVEC_VCMPGTFP_P    = 99
INTR_PPC_ALTIVEC_VCMPGTSB      = 100
INTR_PPC_ALTIVEC_VCMPGTSB_P    = 101
INTR_PPC_ALTIVEC_VCMPGTSH      = 102
INTR_PPC_ALTIVEC_VCMPGTSH_P    = 103
INTR_PPC_ALTIVEC_VCMPGTSW      = 104
INTR_PPC_ALTIVEC_VCMPGTSW_P    = 105
INTR_PPC_ALTIVEC_VCMPGTUB      = 106
INTR_PPC_ALTIVEC_VCMPGTUB_P    = 107
INTR_PPC_ALTIVEC_VCMPGTUH      = 108
INTR_PPC_ALTIVEC_VCMPGTUH_P    = 109
INTR_PPC_ALTIVEC_VCMPGTUW      = 110
INTR_PPC_ALTIVEC_VCMPGTUW_P    = 111
INTR_PPC_ALTIVEC_VCTSXS        = 112
INTR_PPC_ALTIVEC_VCTUXS        = 113
INTR_PPC_ALTIVEC_VEXPTEFP      = 114
INTR_PPC_ALTIVEC_VLOGEFP       = 115
INTR_PPC_ALTIVEC_VMADDFP       = 116
INTR_PPC_ALTIVEC_VMAXFP        = 117
INTR_PPC_ALTIVEC_VMAXSB        = 118
INTR_PPC_ALTIVEC_VMAXSH        = 119
INTR_PPC_ALTIVEC_VMAXSW        = 120
INTR_PPC_ALTIVEC_VMAXUB        = 121
INTR_PPC_ALTIVEC_VMAXUH        = 122
INTR_PPC_ALTIVEC_VMAXUW        = 123
INTR_PPC_ALTIVEC_VMHADDSHS     = 124
INTR_PPC_ALTIVEC_VMHRADDSHS    = 125
INTR_PPC_ALTIVEC_VMINFP        = 126
INTR_PPC_ALTIVEC_VMINSB        = 127
INTR_PPC_ALTIVEC_VMINSH        = 128
INTR_PPC_ALTIVEC_VMINSW        = 129
INTR_PPC_ALTIVEC_VMINUB        = 130
INTR_PPC_ALTIVEC_VMINUH        = 131
INTR_PPC_ALTIVEC_VMINUW        = 132
INTR_PPC_ALTIVEC_VMLADDUHM     = 133
INTR_PPC_ALTIVEC_VMSUMMBM      = 134
INTR_PPC_ALTIVEC_VMSUMSHM      = 135
INTR_PPC_ALTIVEC_VMSUMSHS      = 136
INTR_PPC_ALTIVEC_VMSUMUBM      = 137
INTR_PPC_ALTIVEC_VMSUMUHM      = 138
INTR_PPC_ALTIVEC_VMSUMUHS      = 139
INTR_PPC_ALTIVEC_VMULESB       = 140
INTR_PPC_ALTIVEC_VMULESH       = 141
INTR_PPC_ALTIVEC_VMULEUB       = 142
INTR_PPC_ALTIVEC_VMULEUH       = 143
INTR_PPC_ALTIVEC_VMULOSB       = 144
INTR_PPC_ALTIVEC_VMULOSH       = 145
INTR_PPC_ALTIVEC_VMULOUB       = 146
INTR_PPC_ALTIVEC_VMULOUH       = 147
INTR_PPC_ALTIVEC_VNMSUBFP      = 148
INTR_PPC_ALTIVEC_VPERM         = 149
INTR_PPC_ALTIVEC_VPKPX         = 150
INTR_PPC_ALTIVEC_VPKSHSS       = 151
INTR_PPC_ALTIVEC_VPKSHUS       = 152
INTR_PPC_ALTIVEC_VPKSWSS       = 153
INTR_PPC_ALTIVEC_VPKSWUS       = 154
INTR_PPC_ALTIVEC_VPKUHUS       = 155
INTR_PPC_ALTIVEC_VPKUWUS       = 156
INTR_PPC_ALTIVEC_VREFP         = 157
INTR_PPC_ALTIVEC_VRFIM         = 158
INTR_PPC_ALTIVEC_VRFIN         = 159
INTR_PPC_ALTIVEC_VRFIP         = 160
INTR_PPC_ALTIVEC_VRFIZ         = 161
INTR_PPC_ALTIVEC_VRLB          = 162
INTR_PPC_ALTIVEC_VRLH          = 163
INTR_PPC_ALTIVEC_VRLW          = 164
INTR_PPC_ALTIVEC_VRSQRTEFP     = 165
INTR_PPC_ALTIVEC_VSEL          = 166
INTR_PPC_ALTIVEC_VSL           = 167
INTR_PPC_ALTIVEC_VSLB          = 168
INTR_PPC_ALTIVEC_VSLH          = 169
INTR_PPC_ALTIVEC_VSLO          = 170
INTR_PPC_ALTIVEC_VSLW          = 171
INTR_PPC_ALTIVEC_VSR           = 172
INTR_PPC_ALTIVEC_VSRAB         = 173
INTR_PPC_ALTIVEC_VSRAH         = 174
INTR_PPC_ALTIVEC_VSRAW         = 175
INTR_PPC_ALTIVEC_VSRB          = 176
INTR_PPC_ALTIVEC_VSRH          = 177
INTR_PPC_ALTIVEC_VSRO          = 178
INTR_PPC_ALTIVEC_VSRW          = 179
INTR_PPC_ALTIVEC_VSUBCUW       = 180
INTR_PPC_ALTIVEC_VSUBSBS       = 181
INTR_PPC_ALTIVEC_VSUBSHS       = 182
INTR_PPC_ALTIVEC_VSUBSWS       = 183
INTR_PPC_ALTIVEC_VSUBUBS       = 184
INTR_PPC_ALTIVEC_VSUBUHS       = 185
INTR_PPC_ALTIVEC_VSUBUWS       = 186
INTR_PPC_ALTIVEC_VSUM2SWS      = 187
INTR_PPC_ALTIVEC_VSUM4SBS      = 188
INTR_PPC_ALTIVEC_VSUM4SHS      = 189
INTR_PPC_ALTIVEC_VSUM4UBS      = 190
INTR_PPC_ALTIVEC_VSUMSWS       = 191
INTR_PPC_ALTIVEC_VUPKHPX       = 192
INTR_PPC_ALTIVEC_VUPKHSB       = 193
INTR_PPC_ALTIVEC_VUPKHSH       = 194
INTR_PPC_ALTIVEC_VUPKLPX       = 195
INTR_PPC_ALTIVEC_VUPKLSB       = 196
INTR_PPC_ALTIVEC_VUPKLSH       = 197
INTR_PPC_DCBA                  = 198
INTR_PPC_DCBF                  = 199
INTR_PPC_DCBI                  = 200
INTR_PPC_DCBST                 = 201
INTR_PPC_DCBT                  = 202
INTR_PPC_DCBTST                = 203
INTR_PPC_DCBZ                  = 204
INTR_PPC_DCBZL                 = 205
INTR_PREFETCH                  = 206
INTR_READCYCLECOUNTER          = 207
INTR_RETURNADDRESS             = 208
INTR_SETJMP                    = 209
INTR_SIGLONGJMP                = 210
INTR_SIGSETJMP                 = 211
INTR_SIN                       = 212
INTR_SPU_SI_A                  = 213
INTR_SPU_SI_ADDX               = 214
INTR_SPU_SI_AH                 = 215
INTR_SPU_SI_AHI                = 216
INTR_SPU_SI_AI                 = 217
INTR_SPU_SI_AND                = 218
INTR_SPU_SI_ANDBI              = 219
INTR_SPU_SI_ANDC               = 220
INTR_SPU_SI_ANDHI              = 221
INTR_SPU_SI_ANDI               = 222
INTR_SPU_SI_BG                 = 223
INTR_SPU_SI_BGX                = 224
INTR_SPU_SI_CEQ                = 225
INTR_SPU_SI_CEQB               = 226
INTR_SPU_SI_CEQBI              = 227
INTR_SPU_SI_CEQH               = 228
INTR_SPU_SI_CEQHI              = 229
INTR_SPU_SI_CEQI               = 230
INTR_SPU_SI_CG                 = 231
INTR_SPU_SI_CGT                = 232
INTR_SPU_SI_CGTB               = 233
INTR_SPU_SI_CGTBI              = 234
INTR_SPU_SI_CGTH               = 235
INTR_SPU_SI_CGTHI              = 236
INTR_SPU_SI_CGTI               = 237
INTR_SPU_SI_CGX                = 238
INTR_SPU_SI_CLGT               = 239
INTR_SPU_SI_CLGTB              = 240
INTR_SPU_SI_CLGTBI             = 241
INTR_SPU_SI_CLGTH              = 242
INTR_SPU_SI_CLGTHI             = 243
INTR_SPU_SI_CLGTI              = 244
INTR_SPU_SI_DFA                = 245
INTR_SPU_SI_DFM                = 246
INTR_SPU_SI_DFMA               = 247
INTR_SPU_SI_DFMS               = 248
INTR_SPU_SI_DFNMA              = 249
INTR_SPU_SI_DFNMS              = 250
INTR_SPU_SI_DFS                = 251
INTR_SPU_SI_FA                 = 252
INTR_SPU_SI_FCEQ               = 253
INTR_SPU_SI_FCGT               = 254
INTR_SPU_SI_FCMEQ              = 255
INTR_SPU_SI_FCMGT              = 256
INTR_SPU_SI_FM                 = 257
INTR_SPU_SI_FMA                = 258
INTR_SPU_SI_FMS                = 259
INTR_SPU_SI_FNMS               = 260
INTR_SPU_SI_FS                 = 261
INTR_SPU_SI_FSMBI              = 262
INTR_SPU_SI_MPY                = 263
INTR_SPU_SI_MPYA               = 264
INTR_SPU_SI_MPYH               = 265
INTR_SPU_SI_MPYHH              = 266
INTR_SPU_SI_MPYHHA             = 267
INTR_SPU_SI_MPYHHAU            = 268
INTR_SPU_SI_MPYHHU             = 269
INTR_SPU_SI_MPYI               = 270
INTR_SPU_SI_MPYS               = 271
INTR_SPU_SI_MPYU               = 272
INTR_SPU_SI_MPYUI              = 273
INTR_SPU_SI_NAND               = 274
INTR_SPU_SI_NOR                = 275
INTR_SPU_SI_OR                 = 276
INTR_SPU_SI_ORBI               = 277
INTR_SPU_SI_ORC                = 278
INTR_SPU_SI_ORHI               = 279
INTR_SPU_SI_ORI                = 280
INTR_SPU_SI_SF                 = 281
INTR_SPU_SI_SFH                = 282
INTR_SPU_SI_SFHI               = 283
INTR_SPU_SI_SFI                = 284
INTR_SPU_SI_SFX                = 285
INTR_SPU_SI_SHLI               = 286
INTR_SPU_SI_SHLQBI             = 287
INTR_SPU_SI_SHLQBII            = 288
INTR_SPU_SI_SHLQBY             = 289
INTR_SPU_SI_SHLQBYI            = 290
INTR_SPU_SI_XOR                = 291
INTR_SPU_SI_XORBI              = 292
INTR_SPU_SI_XORHI              = 293
INTR_SPU_SI_XORI               = 294
INTR_SQRT                      = 295
INTR_STACKRESTORE              = 296
INTR_STACKSAVE                 = 297
INTR_TRAP                      = 298
INTR_VACOPY                    = 299
INTR_VAEND                     = 300
INTR_VAR_ANNOTATION            = 301
INTR_VASTART                   = 302
INTR_X86_MMX_EMMS              = 303
INTR_X86_MMX_FEMMS             = 304
INTR_X86_MMX_MASKMOVQ          = 305
INTR_X86_MMX_MOVNT_DQ          = 306
INTR_X86_MMX_PACKSSDW          = 307
INTR_X86_MMX_PACKSSWB          = 308
INTR_X86_MMX_PACKUSWB          = 309
INTR_X86_MMX_PADDS_B           = 310
INTR_X86_MMX_PADDS_W           = 311
INTR_X86_MMX_PADDUS_B          = 312
INTR_X86_MMX_PADDUS_W          = 313
INTR_X86_MMX_PAVG_B            = 314
INTR_X86_MMX_PAVG_W            = 315
INTR_X86_MMX_PCMPEQ_B          = 316
INTR_X86_MMX_PCMPEQ_D          = 317
INTR_X86_MMX_PCMPEQ_W          = 318
INTR_X86_MMX_PCMPGT_B          = 319
INTR_X86_MMX_PCMPGT_D          = 320
INTR_X86_MMX_PCMPGT_W          = 321
INTR_X86_MMX_PMADD_WD          = 322
INTR_X86_MMX_PMAXS_W           = 323
INTR_X86_MMX_PMAXU_B           = 324
INTR_X86_MMX_PMINS_W           = 325
INTR_X86_MMX_PMINU_B           = 326
INTR_X86_MMX_PMOVMSKB          = 327
INTR_X86_MMX_PMULH_W           = 328
INTR_X86_MMX_PMULHU_W          = 329
INTR_X86_MMX_PMULU_DQ          = 330
INTR_X86_MMX_PSAD_BW           = 331
INTR_X86_MMX_PSLL_D            = 332
INTR_X86_MMX_PSLL_Q            = 333
INTR_X86_MMX_PSLL_W            = 334
INTR_X86_MMX_PSLLI_D           = 335
INTR_X86_MMX_PSLLI_Q           = 336
INTR_X86_MMX_PSLLI_W           = 337
INTR_X86_MMX_PSRA_D            = 338
INTR_X86_MMX_PSRA_W            = 339
INTR_X86_MMX_PSRAI_D           = 340
INTR_X86_MMX_PSRAI_W           = 341
INTR_X86_MMX_PSRL_D            = 342
INTR_X86_MMX_PSRL_Q            = 343
INTR_X86_MMX_PSRL_W            = 344
INTR_X86_MMX_PSRLI_D           = 345
INTR_X86_MMX_PSRLI_Q           = 346
INTR_X86_MMX_PSRLI_W           = 347
INTR_X86_MMX_PSUBS_B           = 348
INTR_X86_MMX_PSUBS_W           = 349
INTR_X86_MMX_PSUBUS_B          = 350
INTR_X86_MMX_PSUBUS_W          = 351
INTR_X86_SSE2_ADD_SD           = 352
INTR_X86_SSE2_CLFLUSH          = 353
INTR_X86_SSE2_CMP_PD           = 354
INTR_X86_SSE2_CMP_SD           = 355
INTR_X86_SSE2_COMIEQ_SD        = 356
INTR_X86_SSE2_COMIGE_SD        = 357
INTR_X86_SSE2_COMIGT_SD        = 358
INTR_X86_SSE2_COMILE_SD        = 359
INTR_X86_SSE2_COMILT_SD        = 360
INTR_X86_SSE2_COMINEQ_SD       = 361
INTR_X86_SSE2_CVTDQ2PD         = 362
INTR_X86_SSE2_CVTDQ2PS         = 363
INTR_X86_SSE2_CVTPD2DQ         = 364
INTR_X86_SSE2_CVTPD2PS         = 365
INTR_X86_SSE2_CVTPS2DQ         = 366
INTR_X86_SSE2_CVTPS2PD         = 367
INTR_X86_SSE2_CVTSD2SI         = 368
INTR_X86_SSE2_CVTSD2SI64       = 369
INTR_X86_SSE2_CVTSD2SS         = 370
INTR_X86_SSE2_CVTSI2SD         = 371
INTR_X86_SSE2_CVTSI642SD       = 372
INTR_X86_SSE2_CVTSS2SD         = 373
INTR_X86_SSE2_CVTTPD2DQ        = 374
INTR_X86_SSE2_CVTTPS2DQ        = 375
INTR_X86_SSE2_CVTTSD2SI        = 376
INTR_X86_SSE2_CVTTSD2SI64      = 377
INTR_X86_SSE2_DIV_SD           = 378
INTR_X86_SSE2_LFENCE           = 379
INTR_X86_SSE2_LOADH_PD         = 380
INTR_X86_SSE2_LOADL_PD         = 381
INTR_X86_SSE2_LOADU_DQ         = 382
INTR_X86_SSE2_LOADU_PD         = 383
INTR_X86_SSE2_MASKMOV_DQU      = 384
INTR_X86_SSE2_MAX_PD           = 385
INTR_X86_SSE2_MAX_SD           = 386
INTR_X86_SSE2_MFENCE           = 387
INTR_X86_SSE2_MIN_PD           = 388
INTR_X86_SSE2_MIN_SD           = 389
INTR_X86_SSE2_MOVMSK_PD        = 390
INTR_X86_SSE2_MOVNT_DQ         = 391
INTR_X86_SSE2_MOVNT_I          = 392
INTR_X86_SSE2_MOVNT_PD         = 393
INTR_X86_SSE2_MOVS_D           = 394
INTR_X86_SSE2_MUL_SD           = 395
INTR_X86_SSE2_PACKSSDW_128     = 396
INTR_X86_SSE2_PACKSSWB_128     = 397
INTR_X86_SSE2_PACKUSWB_128     = 398
INTR_X86_SSE2_PADDS_B          = 399
INTR_X86_SSE2_PADDS_W          = 400
INTR_X86_SSE2_PADDUS_B         = 401
INTR_X86_SSE2_PADDUS_W         = 402
INTR_X86_SSE2_PAVG_B           = 403
INTR_X86_SSE2_PAVG_W           = 404
INTR_X86_SSE2_PCMPEQ_B         = 405
INTR_X86_SSE2_PCMPEQ_D         = 406
INTR_X86_SSE2_PCMPEQ_W         = 407
INTR_X86_SSE2_PCMPGT_B         = 408
INTR_X86_SSE2_PCMPGT_D         = 409
INTR_X86_SSE2_PCMPGT_W         = 410
INTR_X86_SSE2_PMADD_WD         = 411
INTR_X86_SSE2_PMAXS_W          = 412
INTR_X86_SSE2_PMAXU_B          = 413
INTR_X86_SSE2_PMINS_W          = 414
INTR_X86_SSE2_PMINU_B          = 415
INTR_X86_SSE2_PMOVMSKB_128     = 416
INTR_X86_SSE2_PMULH_W          = 417
INTR_X86_SSE2_PMULHU_W         = 418
INTR_X86_SSE2_PMULU_DQ         = 419
INTR_X86_SSE2_PSAD_BW          = 420
INTR_X86_SSE2_PSLL_D           = 421
INTR_X86_SSE2_PSLL_DQ          = 422
INTR_X86_SSE2_PSLL_Q           = 423
INTR_X86_SSE2_PSLL_W           = 424
INTR_X86_SSE2_PSLLI_D          = 425
INTR_X86_SSE2_PSLLI_Q          = 426
INTR_X86_SSE2_PSLLI_W          = 427
INTR_X86_SSE2_PSRA_D           = 428
INTR_X86_SSE2_PSRA_W           = 429
INTR_X86_SSE2_PSRAI_D          = 430
INTR_X86_SSE2_PSRAI_W          = 431
INTR_X86_SSE2_PSRL_D           = 432
INTR_X86_SSE2_PSRL_DQ          = 433
INTR_X86_SSE2_PSRL_Q           = 434
INTR_X86_SSE2_PSRL_W           = 435
INTR_X86_SSE2_PSRLI_D          = 436
INTR_X86_SSE2_PSRLI_Q          = 437
INTR_X86_SSE2_PSRLI_W          = 438
INTR_X86_SSE2_PSUBS_B          = 439
INTR_X86_SSE2_PSUBS_W          = 440
INTR_X86_SSE2_PSUBUS_B         = 441
INTR_X86_SSE2_PSUBUS_W         = 442
INTR_X86_SSE2_PUNPCKH_QDQ      = 443
INTR_X86_SSE2_PUNPCKL_QDQ      = 444
INTR_X86_SSE2_SHUF_PD          = 445
INTR_X86_SSE2_SQRT_PD          = 446
INTR_X86_SSE2_SQRT_SD          = 447
INTR_X86_SSE2_STOREL_DQ        = 448
INTR_X86_SSE2_STOREU_DQ        = 449
INTR_X86_SSE2_STOREU_PD        = 450
INTR_X86_SSE2_SUB_SD           = 451
INTR_X86_SSE2_UCOMIEQ_SD       = 452
INTR_X86_SSE2_UCOMIGE_SD       = 453
INTR_X86_SSE2_UCOMIGT_SD       = 454
INTR_X86_SSE2_UCOMILE_SD       = 455
INTR_X86_SSE2_UCOMILT_SD       = 456
INTR_X86_SSE2_UCOMINEQ_SD      = 457
INTR_X86_SSE2_UNPCKH_PD        = 458
INTR_X86_SSE2_UNPCKL_PD        = 459
INTR_X86_SSE3_ADDSUB_PD        = 460
INTR_X86_SSE3_ADDSUB_PS        = 461
INTR_X86_SSE3_HADD_PD          = 462
INTR_X86_SSE3_HADD_PS          = 463
INTR_X86_SSE3_HSUB_PD          = 464
INTR_X86_SSE3_HSUB_PS          = 465
INTR_X86_SSE3_LDU_DQ           = 466
INTR_X86_SSE3_MONITOR          = 467
INTR_X86_SSE3_MWAIT            = 468
INTR_X86_SSE41_BLENDPD         = 469
INTR_X86_SSE41_BLENDPS         = 470
INTR_X86_SSE41_BLENDVPD        = 471
INTR_X86_SSE41_BLENDVPS        = 472
INTR_X86_SSE41_DPPD            = 473
INTR_X86_SSE41_DPPS            = 474
INTR_X86_SSE41_EXTRACTPS       = 475
INTR_X86_SSE41_INSERTPS        = 476
INTR_X86_SSE41_MOVNTDQA        = 477
INTR_X86_SSE41_MPSADBW         = 478
INTR_X86_SSE41_PACKUSDW        = 479
INTR_X86_SSE41_PBLENDVB        = 480
INTR_X86_SSE41_PBLENDW         = 481
INTR_X86_SSE41_PCMPEQQ         = 482
INTR_X86_SSE41_PEXTRB          = 483
INTR_X86_SSE41_PEXTRD          = 484
INTR_X86_SSE41_PEXTRQ          = 485
INTR_X86_SSE41_PHMINPOSUW      = 486
INTR_X86_SSE41_PINSRB          = 487
INTR_X86_SSE41_PINSRD          = 488
INTR_X86_SSE41_PINSRQ          = 489
INTR_X86_SSE41_PMAXSB          = 490
INTR_X86_SSE41_PMAXSD          = 491
INTR_X86_SSE41_PMAXUD          = 492
INTR_X86_SSE41_PMAXUW          = 493
INTR_X86_SSE41_PMINSB          = 494
INTR_X86_SSE41_PMINSD          = 495
INTR_X86_SSE41_PMINUD          = 496
INTR_X86_SSE41_PMINUW          = 497
INTR_X86_SSE41_PMOVSXBD        = 498
INTR_X86_SSE41_PMOVSXBQ        = 499
INTR_X86_SSE41_PMOVSXBW        = 500
INTR_X86_SSE41_PMOVSXDQ        = 501
INTR_X86_SSE41_PMOVSXWD        = 502
INTR_X86_SSE41_PMOVSXWQ        = 503
INTR_X86_SSE41_PMOVZXBD        = 504
INTR_X86_SSE41_PMOVZXBQ        = 505
INTR_X86_SSE41_PMOVZXBW        = 506
INTR_X86_SSE41_PMOVZXDQ        = 507
INTR_X86_SSE41_PMOVZXWD        = 508
INTR_X86_SSE41_PMOVZXWQ        = 509
INTR_X86_SSE41_PMULDQ          = 510
INTR_X86_SSE41_PMULLD          = 511
INTR_X86_SSE41_ROUND_PD        = 512
INTR_X86_SSE41_ROUND_PS        = 513
INTR_X86_SSE41_ROUND_SD        = 514
INTR_X86_SSE41_ROUND_SS        = 515
INTR_X86_SSE_ADD_SS            = 516
INTR_X86_SSE_CMP_PS            = 517
INTR_X86_SSE_CMP_SS            = 518
INTR_X86_SSE_COMIEQ_SS         = 519
INTR_X86_SSE_COMIGE_SS         = 520
INTR_X86_SSE_COMIGT_SS         = 521
INTR_X86_SSE_COMILE_SS         = 522
INTR_X86_SSE_COMILT_SS         = 523
INTR_X86_SSE_COMINEQ_SS        = 524
INTR_X86_SSE_CVTPD2PI          = 525
INTR_X86_SSE_CVTPI2PD          = 526
INTR_X86_SSE_CVTPI2PS          = 527
INTR_X86_SSE_CVTPS2PI          = 528
INTR_X86_SSE_CVTSI2SS          = 529
INTR_X86_SSE_CVTSI642SS        = 530
INTR_X86_SSE_CVTSS2SI          = 531
INTR_X86_SSE_CVTSS2SI64        = 532
INTR_X86_SSE_CVTTPD2PI         = 533
INTR_X86_SSE_CVTTPS2PI         = 534
INTR_X86_SSE_CVTTSS2SI         = 535
INTR_X86_SSE_CVTTSS2SI64       = 536
INTR_X86_SSE_DIV_SS            = 537
INTR_X86_SSE_LDMXCSR           = 538
INTR_X86_SSE_LOADU_PS          = 539
INTR_X86_SSE_MAX_PS            = 540
INTR_X86_SSE_MAX_SS            = 541
INTR_X86_SSE_MIN_PS            = 542
INTR_X86_SSE_MIN_SS            = 543
INTR_X86_SSE_MOVMSK_PS         = 544
INTR_X86_SSE_MOVNT_PS          = 545
INTR_X86_SSE_MUL_SS            = 546
INTR_X86_SSE_RCP_PS            = 547
INTR_X86_SSE_RCP_SS            = 548
INTR_X86_SSE_RSQRT_PS          = 549
INTR_X86_SSE_RSQRT_SS          = 550
INTR_X86_SSE_SFENCE            = 551
INTR_X86_SSE_SQRT_PS           = 552
INTR_X86_SSE_SQRT_SS           = 553
INTR_X86_SSE_STMXCSR           = 554
INTR_X86_SSE_STOREU_PS         = 555
INTR_X86_SSE_SUB_SS            = 556
INTR_X86_SSE_UCOMIEQ_SS        = 557
INTR_X86_SSE_UCOMIGE_SS        = 558
INTR_X86_SSE_UCOMIGT_SS        = 559
INTR_X86_SSE_UCOMILE_SS        = 560
INTR_X86_SSE_UCOMILT_SS        = 561
INTR_X86_SSE_UCOMINEQ_SS       = 562
INTR_X86_SSSE3_PABS_B          = 563
INTR_X86_SSSE3_PABS_B_128      = 564
INTR_X86_SSSE3_PABS_D          = 565
INTR_X86_SSSE3_PABS_D_128      = 566
INTR_X86_SSSE3_PABS_W          = 567
INTR_X86_SSSE3_PABS_W_128      = 568
INTR_X86_SSSE3_PALIGN_R        = 569
INTR_X86_SSSE3_PALIGN_R_128    = 570
INTR_X86_SSSE3_PHADD_D         = 571
INTR_X86_SSSE3_PHADD_D_128     = 572
INTR_X86_SSSE3_PHADD_SW        = 573
INTR_X86_SSSE3_PHADD_SW_128    = 574
INTR_X86_SSSE3_PHADD_W         = 575
INTR_X86_SSSE3_PHADD_W_128     = 576
INTR_X86_SSSE3_PHSUB_D         = 577
INTR_X86_SSSE3_PHSUB_D_128     = 578
INTR_X86_SSSE3_PHSUB_SW        = 579
INTR_X86_SSSE3_PHSUB_SW_128    = 580
INTR_X86_SSSE3_PHSUB_W         = 581
INTR_X86_SSSE3_PHSUB_W_128     = 582
INTR_X86_SSSE3_PMADD_UB_SW     = 583
INTR_X86_SSSE3_PMADD_UB_SW_128 = 584
INTR_X86_SSSE3_PMUL_HR_SW      = 585
INTR_X86_SSSE3_PMUL_HR_SW_128  = 586
INTR_X86_SSSE3_PSHUF_B         = 587
INTR_X86_SSSE3_PSHUF_B_128     = 588
INTR_X86_SSSE3_PSIGN_B         = 589
INTR_X86_SSSE3_PSIGN_B_128     = 590
INTR_X86_SSSE3_PSIGN_D         = 591
INTR_X86_SSSE3_PSIGN_D_128     = 592
INTR_X86_SSSE3_PSIGN_W         = 593
INTR_X86_SSSE3_PSIGN_W_128     = 594


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
            self.ptr, GlobalVariable, [self])

    def add_function(self, ty, name):
        """Add a function of given type with given name."""
        return Function.new(self, ty, name)

    def get_function_named(self, name):
        """Return a Function object representing function with given name."""
        return Function.get(self, name)

    def get_or_insert_function(self, ty, name):
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
            _core.LLVMGetNextFunction, self.ptr, Function, [self])

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
        var_arg = 1 if var_arg else 0 # convert to int
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

    def __init__(self, ptr, kind):
        """DO NOT CALL DIRECTLY.

        Use one of the static methods of the *base* class (Type) instead."""
        Type.__init__(self, ptr, kind)

    @property
    def element_count(self):
        return _core.LLVMCountStructElementTypes(self.ptr)

    @property
    def elements(self):
        pp = _core.LLVMGetStructElementTypes(self.ptr)
        return [ _make_type(p, _core.LLVMGetTypeKind(p)) for p in pp ]

    @property
    def packed(self):
        return _core.LLVMIsPackedStruct(self.ptr) != 0


class ArrayType(Type):

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

    def __init__(self, ptr):
        self.ptr = ptr

    def __str__(self):
        return _core.LLVMDumpValueToString(self.ptr)

    def __eq__(self, rhs):
        if isinstance(rhs, Value):
            return str(self) == str(rhs)
        else:
            return False

    def _get_name(self):
        return _core.LLVMGetValueName(self.ptr)

    def _set_name(self, value):
        return _core.LLVMSetValueName(self.ptr, value)

    name = property(_get_name, _set_name)

    @property
    def type(self):
        ptr  = _core.LLVMTypeOf(self.ptr)
        kind = _core.LLVMGetTypeKind(ptr)
        return _make_type(ptr, kind)


class Constant(Value):

    @staticmethod
    def null(ty):
        check_is_type(ty)
        return Constant(_core.LLVMConstNull(ty.ptr));
        
    @staticmethod
    def all_ones(ty):
        check_is_type(ty)
        return Constant(_core.LLVMConstAllOnes(ty.ptr));
        
    @staticmethod
    def undef(ty):
        check_is_type(ty)
        return Constant(_core.LLVMGetUndef(ty.ptr));

    @staticmethod
    def int(ty, value):
        check_is_type(ty)
        return Constant(_core.LLVMConstInt(ty.ptr, value, 0))

    @staticmethod
    def int_signextend(ty, value):
        check_is_type(ty)
        return Constant(_core.LLVMConstInt(ty.ptr, value, 1))

    @staticmethod
    def real(ty, value):
        check_is_type(ty)
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
        check_is_type(ty)
        const_ptrs = unpack_constants(consts)
        return Constant(_core.LLVMConstArray(ty.ptr, const_ptrs))
        
    @staticmethod
    def struct(consts): # not packed
        const_ptrs = unpack_constants(consts)
        return Constant(_core.LLVMConstStruct(const_ptrs, 0))
    
    @staticmethod
    def packed_struct(consts):
        const_ptrs = unpack_constants(consts)
        return Constant(_core.LLVMConstStruct(const_ptrs, 1))
    
    @staticmethod
    def vector(consts):
        const_ptrs = unpack_constants(consts)
        return Constant(_core.LLVMConstVector(const_ptrs))

    @staticmethod
    def sizeof(ty):
        check_is_type(ty)
        return Constant(_core.LLVMSizeOf(ty.ptr))

    def __init__(self, ptr):
        Value.__init__(self, ptr)
        
    def neg(self):
        return Constant(_core.LLVMConstNeg(self.ptr))
        
    def not_(self):
        return Constant(_core.LLVMConstNot(self.ptr))
        
    def add(self, rhs):
        check_is_constant(rhs)
        return Constant(_core.LLVMConstAdd(self.ptr, rhs.ptr))

    def sub(self, rhs):
        check_is_constant(rhs)
        return Constant(_core.LLVMConstSub(self.ptr, rhs.ptr))

    def mul(self, rhs):
        check_is_constant(rhs)
        return Constant(_core.LLVMConstMul(self.ptr, rhs.ptr))

    def udiv(self, rhs):
        check_is_constant(rhs)
        return Constant(_core.LLVMConstUDiv(self.ptr, rhs.ptr))

    def sdiv(self, rhs):
        check_is_constant(rhs)
        return Constant(_core.LLVMConstSDiv(self.ptr, rhs.ptr))

    def fdiv(self, rhs):
        check_is_constant(rhs)
        return Constant(_core.LLVMConstFDiv(self.ptr, rhs.ptr))

    def urem(self, rhs):
        check_is_constant(rhs)
        return Constant(_core.LLVMConstURem(self.ptr, rhs.ptr))

    def srem(self, rhs):
        check_is_constant(rhs)
        return Constant(_core.LLVMConstSRem(self.ptr, rhs.ptr))

    def frem(self, rhs):
        check_is_constant(rhs)
        return Constant(_core.LLVMConstFRem(self.ptr, rhs.ptr))

    def and_(self, rhs):
        check_is_constant(rhs)
        return Constant(_core.LLVMConstAnd(self.ptr, rhs.ptr))

    def or_(self, rhs):
        check_is_constant(rhs)
        return Constant(_core.LLVMConstOr(self.ptr, rhs.ptr))

    def xor(self, rhs):
        check_is_constant(rhs)
        return Constant(_core.LLVMConstXor(self.ptr, rhs.ptr))

    def icmp(self, int_pred, rhs):
        check_is_constant(rhs)
        return Constant(_core.LLVMConstICmp(int_pred, self.ptr, rhs.ptr))

    def fcmp(self, real_pred, rhs):
        check_is_constant(rhs)
        return Constant(_core.LLVMConstFCmp(real_pred, self.ptr, rhs.ptr))

# after LLVM 2.3!
#    def vicmp(self, int_pred, rhs):
#        check_is_constant(rhs)
#        return Constant(_core.LLVMConstVICmp(int_pred, self.ptr, rhs.ptr))
#
#    def vfcmp(self, real_pred, rhs):
#        check_is_constant(rhs)
#        return Constant(_core.LLVMConstVFCmp(real_pred, self.ptr, rhs.ptr))

    def shl(self, rhs):
        check_is_constant(rhs)
        return Constant(_core.LLVMConstShl(self.ptr, rhs.ptr))

    def lshr(self, rhs):
        check_is_constant(rhs)
        return Constant(_core.LLVMConstLShr(self.ptr, rhs.ptr))

    def ashr(self, rhs):
        check_is_constant(rhs)
        return Constant(_core.LLVMConstAShr(self.ptr, rhs.ptr))

    def gep(self, indices):
        index_ptrs = unpack_constants(indices)
        return Constant(_core.LLVMConstGEP(self.ptr, index_ptrs))
    
    def trunc(self, ty):
        check_is_type(ty)
        return Constant(_core.LLVMConstTrunc(self.ptr, ty.ptr))

    def sext(self, ty):
        check_is_type(ty)
        return Constant(_core.LLVMConstSExt(self.ptr, ty.ptr))

    def zext(self, ty):
        check_is_type(ty)
        return Constant(_core.LLVMConstZExt(self.ptr, ty.ptr))

    def fptrunc(self, ty):
        check_is_type(ty)
        return Constant(_core.LLVMConstFPTrunc(self.ptr, ty.ptr))

    def fpext(self, ty):
        check_is_type(ty)
        return Constant(_core.LLVMConstFPExt(self.ptr, ty.ptr))

    def uitofp(self, ty):
        check_is_type(ty)
        return Constant(_core.LLVMConstUIToFP(self.ptr, ty.ptr))

    def sitofp(self, ty):
        check_is_type(ty)
        return Constant(_core.LLVMConstSIToFP(self.ptr, ty.ptr))

    def fptoui(self, ty):
        check_is_type(ty)
        return Constant(_core.LLVMConstFPToUI(self.ptr, ty.ptr))

    def fptosi(self, ty):
        check_is_type(ty)
        return Constant(_core.LLVMConstFPToSI(self.ptr, ty.ptr))

    def ptrtoint(self, ty):
        check_is_type(ty)
        return Constant(_core.LLVMConstPtrToInt(self.ptr, ty.ptr))

    def inttoptr(self, ty):
        check_is_type(ty)
        return Constant(_core.LLVMConstIntToPtr(self.ptr, ty.ptr))

    def bitcast(self, ty):
        check_is_type(ty)
        return Constant(_core.LLVMConstBitCast(self.ptr, ty.ptr))

    def select(self, true_const, false_const):
        check_is_constant(true_const)
        check_is_constant(false_const)
        return Constant(_core.LLVMConstSelect(self.ptr, true_const.ptr, false_const.ptr))

    def extract_element(self, index): # note: self must be a _vector_ constant
        check_is_constant(index)
        return Constant(_core.LLVMConstExtractElement(self.ptr, index.ptr))

    def insert_element(self, value, index): # note: self must be a _vector_ constant
        check_is_constant(value)
        check_is_constant(index)
        return Constant(_core.LLVMConstInsertElement(self.ptr, value.ptr, index.ptr))

    def shuffle_vector(self, vector_b, mask): # note: self must be a _vector_ constant
        check_is_constant(vector_b)   # note: vector_b must be a _vector_ constant
        check_is_constant(mask)
        return Constant(_core.LLVMConstShuffleVector(self.ptr, vector_b.ptr, mask.ptr))


class GlobalValue(Constant):

    def __init__(self, ptr, module):
        Constant.__init__(self, ptr)
        self._module = module # hang on to the module

    def _delete(self):
        self._module = None # set it free
        self.ptr = None

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
        return self._module


class GlobalVariable(GlobalValue):

    @staticmethod
    def new(module, ty, name):
        check_is_type(ty)
        return GlobalVariable(_core.LLVMAddGlobal(module.ptr, ty.ptr, name), module)

    @staticmethod
    def get(module, name):
        ptr = _core.LLVMGetNamedGlobal(module.ptr, name)
        if not ptr:
            raise llvm.LLVMException, ("no global named `%s`" % name)
        return GlobalVariable(ptr, name)

    def __init__(self, ptr, module):
        GlobalValue.__init__(self, ptr, module)

    def delete(self):
        _core.LLVMDeleteGlobal(self.ptr)
        self._delete()

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
        value = 1 if value else 0
        _core.LLVMSetGlobalConstant(self.ptr, value)

    global_constant = property(_get_is_global_constant, _set_is_global_constant)


class Argument(Value):

    def __init__(self, ptr):
        Value.__init__(self, ptr)

    def add_attribute(self, attr):
        _core.LLVMAddParamAttr(self.ptr, attr)

    def remove_attribute(self, attr):
        _core.LLVMRemoveParamAttr(self.ptr, attr)

    def set_alignment(self, align):
        _core.LLVMSetParamAlignment(self.ptr, align)


class Function(GlobalValue):

    @staticmethod
    def new(module, func_ty, name):
        check_is_module(module)
        check_is_type(func_ty)
        return Function(_core.LLVMAddFunction(module.ptr, name, \
            func_ty.ptr), module)

    @staticmethod
    def get_or_insert(module, func_ty, name):
        check_is_module(module)
        check_is_type(func_ty)
        return Function(_core.LLVMModuleGetOrInsertFunction(module.ptr, \
            name, func_ty.ptr), module)

    @staticmethod
    def get(module, name):
        ptr = _core.LLVMGetNamedFunction(module.ptr, name)
        if not ptr:
            raise llvm.LLVMException, ("no function named `%s`" % name)
        return Function(ptr, module)
    
    @staticmethod
    def intrinsic(module, id, types):
        check_is_module(module)
        ptrs = unpack_types(types)
        return Function(_core.LLVMGetIntrinsic(module.ptr, id, ptrs), module)

    def __init__(self, ptr, module):
        GlobalValue.__init__(self, ptr, module)

    def delete(self):
        _core.LLVMDeleteFunction(self.ptr)
        self._delete()

    @property
    def intrinsic_id(self):
        return _core.LLVMGetIntrinsicID(self.ptr)

    def _get_cc(self): return _core.LLVMGetFunctionCallConv(self.ptr)
    def _set_cc(self, value): _core.LLVMSetFunctionCallConv(self.ptr, value)
    calling_convention = property(_get_cc, _set_cc)

    def _get_coll(self): return _core.LLVMGetCollector(self.ptr)
    def _set_coll(self, value): _core.LLVMSetCollector(self.ptr, value)
    collector = property(_get_coll, _set_coll)

    @property
    def args(self):
        return wrapiter(_core.LLVMGetFirstParam, _core.LLVMGetNextParam,
            self.ptr, Argument)

    @property
    def basic_block_count(self):
        return _core.LLVMCountBasicBlocks(self.ptr)

    def get_entry_basic_block(self):
        if self.basic_block_count == 0:
            return None
        return BasicBlock(_core.LLVMGetEntryBasicBlock(self.ptr))

    def append_basic_block(self, name):
        return BasicBlock(_core.LLVMAppendBasicBlock(self.ptr, name))

    @property
    def basic_blocks(self):
        return wrapiter(_core.LLVMGetFirstBasicBlock, 
            _core.LLVMGetNextBasicBlock, self.ptr, BasicBlock)

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
        return BasicBlock(_core.LLVMGetInstructionParent(self.ptr))

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
    def opcode(self):
        return _core.LLVMInstGetOpcode(self.ptr)

    @property
    def opcode_name(self):
        return _core.LLVMInstGetOpcodeName(self.ptr)


class CallOrInvokeInstruction(Instruction):

    def __init__(self, ptr):
        Instruction.__init__(self, ptr)

    def _get_cc(self): return _core.LLVMGetInstructionCallConv(self.ptr)
    def _set_cc(self, value): _core.LLVMSetInstructionCallConv(self.ptr, value)
    calling_convention = property(_get_cc, _set_cc)

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
        check_is_value(value)
        check_is_basic_block(block)
        _core.LLVMAddIncoming1(self.ptr, value.ptr, block.ptr)

    def get_incoming_value(self, idx):
        return Value(_core.LLVMGetIncomingValue(self.ptr, idx))

    def get_incoming_block(self, idx):
        return BasicBlock(_core.LLVMGetIncomingBlock(self.ptr, idx))


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
        return BasicBlock(_core.LLVMInsertBasicBlock(self.ptr, name))

    def delete(self):
        _core.LLVMDeleteBasicBlock(self.ptr)
        self.ptr = None

    #-- disabled till we find a proper way to do it --
    #@property
    #def function(self):
    #    return Function(_core.LLVMGetBasicBlockParent(self.ptr))

    @property
    def instructions(self):
        return wrapiter(_core.LLVMGetFirstInstruction,
            _core.LLVMGetNextInstruction, self.ptr, Instruction)


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
        first_inst = Instruction(_core.LLVMGetFirstInstruction(self.block.ptr))
        self.position_before(first_inst)

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
        return BasicBlock(_core.LLVMGetInsertBlock(self.ptr))

    # terminator instructions

    def ret_void(self):
        return Instruction(_core.LLVMBuildRetVoid(self.ptr))

    def ret(self, value):
        check_is_value(value)
        return Instruction(_core.LLVMBuildRet(self.ptr, value.ptr))

    def ret_many(self, values):
        vs = unpack_values(values)
        return Instruction(_core.LLVMBuildRetMultiple(self.ptr, vs))

    def branch(self, bblk):
        check_is_basic_block(bblk)
        return Instruction(_core.LLVMBuildBr(self.ptr, bblk.ptr))
        
    def cbranch(self, if_value, then_blk, else_blk):
        check_is_value(if_value)
        check_is_basic_block(then_blk)
        check_is_basic_block(else_blk)
        return Instruction(_core.LLVMBuildCondBr(self.ptr, if_value.ptr, then_blk.ptr, else_blk.ptr))
        
    def switch(self, value, else_blk, n=10):
        check_is_value(value)  # value has to be of any 'int' type
        check_is_basic_block(else_blk)
        return SwitchInstruction(_core.LLVMBuildSwitch(self.ptr, value.ptr, else_blk.ptr, n))
        
    def invoke(self, func, args, then_blk, catch_blk, name=""):
        check_is_callable(func)
        check_is_basic_block(then_blk)
        check_is_basic_block(catch_blk)
        args2 = unpack_values(args)
        return CallOrInvokeInstruction(_core.LLVMBuildInvoke(self.ptr, func.ptr, args2, then_blk.ptr, catch_blk.ptr, name))

    def unwind(self):
        return Instruction(_core.LLVMBuildUnwind(self.ptr))
        
    def unreachable(self):
        return Instruction(_core.LLVMBuildUnreachable(self.ptr))

    # arithmethic, bitwise and logical
    
    def add(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return Value(_core.LLVMBuildAdd(self.ptr, lhs.ptr, rhs.ptr, name))
        
    def sub(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return Value(_core.LLVMBuildSub(self.ptr, lhs.ptr, rhs.ptr, name))

    def mul(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return Value(_core.LLVMBuildMul(self.ptr, lhs.ptr, rhs.ptr, name))

    def udiv(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return Value(_core.LLVMBuildUDiv(self.ptr, lhs.ptr, rhs.ptr, name))

    def sdiv(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return Value(_core.LLVMBuildSDiv(self.ptr, lhs.ptr, rhs.ptr, name))

    def fdiv(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return Value(_core.LLVMBuildFDiv(self.ptr, lhs.ptr, rhs.ptr, name))

    def urem(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return Value(_core.LLVMBuildURem(self.ptr, lhs.ptr, rhs.ptr, name))

    def srem(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return Value(_core.LLVMBuildSRem(self.ptr, lhs.ptr, rhs.ptr, name))

    def frem(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return Value(_core.LLVMBuildFRem(self.ptr, lhs.ptr, rhs.ptr, name))

    def shl(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return Value(_core.LLVMBuildShl(self.ptr, lhs.ptr, rhs.ptr, name))

    def lshr(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return Value(_core.LLVMBuildLShr(self.ptr, lhs.ptr, rhs.ptr, name))

    def ashr(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return Value(_core.LLVMBuildAShr(self.ptr, lhs.ptr, rhs.ptr, name))

    def and_(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return Value(_core.LLVMBuildAnd(self.ptr, lhs.ptr, rhs.ptr, name))

    def or_(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return Value(_core.LLVMBuildOr(self.ptr, lhs.ptr, rhs.ptr, name))

    def xor(self, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return Value(_core.LLVMBuildXor(self.ptr, lhs.ptr, rhs.ptr, name))

    def neg(self, val, name=""):
        check_is_value(val)
        return Instruction(_core.LLVMBuildNeg(self.ptr, val.ptr, name))

    def not_(self, val, name=""):
        check_is_value(val)
        return Instruction(_core.LLVMBuildNot(self.ptr, val.ptr, name))

    # memory

    def malloc(self, ty, name=""):
        check_is_type(ty)
        return Instruction(_core.LLVMBuildMalloc(self.ptr, ty.ptr, name))

    def malloc_array(self, ty, size, name=""):
        check_is_type(ty)
        check_is_value(size)
        return Instruction(_core.LLVMBuildArrayMalloc(self.ptr, ty.ptr, size.ptr, name))

    def alloca(self, ty, name=""):
        check_is_type(ty)
        return Instruction(_core.LLVMBuildAlloca(self.ptr, ty.ptr, name))

    def alloca_array(self, ty, size, name=""):
        check_is_type(ty)
        check_is_value(size)
        return Instruction(_core.LLVMBuildArrayAlloca(self.ptr, ty.ptr, size.ptr, name))

    def free(self, ptr):
        check_is_value(ptr)
        return Instruction(_core.LLVMBuildFree(self.ptr, ptr.ptr))

    def load(self, ptr, name=""):
        check_is_value(ptr)
        return Instruction(_core.LLVMBuildLoad(self.ptr, ptr.ptr, name))

    def store(self, value, ptr):
        check_is_value(value)
        check_is_value(ptr)
        return Instruction(_core.LLVMBuildStore(self.ptr, value.ptr, ptr.ptr))

    def gep(self, ptr, indices, name=""):
        check_is_value(ptr)
        index_ptrs = unpack_values(indices)
        return Value(_core.LLVMBuildGEP(self.ptr, ptr.ptr, index_ptrs, name))

    # casts and extensions

    def trunc(self, value, dest_ty, name=""):
        check_is_value(value)
        check_is_type(dest_ty)
        return Value(_core.LLVMBuildTrunc(self.ptr, value.ptr, dest_ty.ptr, name))

    def zext(self, value, dest_ty, name=""):
        check_is_value(value)
        check_is_type(dest_ty)
        return Value(_core.LLVMBuildZExt(self.ptr, value.ptr, dest_ty.ptr, name))

    def sext(self, value, dest_ty, name=""):
        check_is_value(value)
        check_is_type(dest_ty)
        return Value(_core.LLVMBuildSExt(self.ptr, value.ptr, dest_ty.ptr, name))

    def fptoui(self, value, dest_ty, name=""):
        check_is_value(value)
        check_is_type(dest_ty)
        return Value(_core.LLVMBuildFPToUI(self.ptr, value.ptr, dest_ty.ptr, name))

    def fptosi(self, value, dest_ty, name=""):
        check_is_value(value)
        check_is_type(dest_ty)
        return Value(_core.LLVMBuildFPToSI(self.ptr, value.ptr, dest_ty.ptr, name))

    def uitofp(self, value, dest_ty, name=""):
        check_is_value(value)
        check_is_type(dest_ty)
        return Value(_core.LLVMBuildUIToFP(self.ptr, value.ptr, dest_ty.ptr, name))

    def sitofp(self, value, dest_ty, name=""):
        check_is_value(value)
        check_is_type(dest_ty)
        return Value(_core.LLVMBuildSIToFP(self.ptr, value.ptr, dest_ty.ptr, name))

    def fptrunc(self, value, dest_ty, name=""):
        check_is_value(value)
        check_is_type(dest_ty)
        return Value(_core.LLVMBuildFPTrunc(self.ptr, value.ptr, dest_ty.ptr, name))

    def fpext(self, value, dest_ty, name=""):
        check_is_value(value)
        check_is_type(dest_ty)
        return Value(_core.LLVMBuildFPExt(self.ptr, value.ptr, dest_ty.ptr, name))

    def ptrtoint(self, value, dest_ty, name=""):
        check_is_value(value)
        check_is_type(dest_ty)
        return Value(_core.LLVMBuildPtrToInt(self.ptr, value.ptr, dest_ty.ptr, name))

    def inttoptr(self, value, dest_ty, name=""):
        check_is_value(value)
        check_is_type(dest_ty)
        return Value(_core.LLVMBuildIntToPtr(self.ptr, value.ptr, dest_ty.ptr, name))

    def bitcast(self, value, dest_ty, name=""):
        check_is_value(value)
        check_is_type(dest_ty)
        return Value(_core.LLVMBuildBitCast(self.ptr, value.ptr, dest_ty.ptr, name))

    # comparisons

    def icmp(self, ipred, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return Value(_core.LLVMBuildICmp(self.ptr, ipred, lhs.ptr, rhs.ptr, name))
        
    def fcmp(self, rpred, lhs, rhs, name=""):
        check_is_value(lhs)
        check_is_value(rhs)
        return Value(_core.LLVMBuildFCmp(self.ptr, rpred, lhs.ptr, rhs.ptr, name))

# after LLVM 2.3!
#    def vicmp(self, ipred, lhs, rhs, name=""):
#        check_is_value(lhs)
#        check_is_value(rhs)
#        return Value(_core.LLVMBuildVICmp(self.ptr, ipred, lhs.ptr, rhs.ptr, name))
#        
#    def vfcmp(self, rpred, lhs, rhs, name=""):
#        check_is_value(lhs)
#        check_is_value(rhs)
#        return Value(_core.LLVMBuildVFCmp(self.ptr, rpred, lhs.ptr, rhs.ptr, name))

    # misc

    def getresult(self, retval, idx, name=""):
        check_is_value(retval)
        return PHINode(_core.LLVMBuildGetResult(self.ptr, retval.ptr, idx, name))

    def phi(self, ty, name=""):
        check_is_type(ty)
        return PHINode(_core.LLVMBuildPhi(self.ptr, ty.ptr, name))
        
    def call(self, fn, args, name=""):
        check_is_callable(fn)
        arg_ptrs = unpack_values(args)
        return CallOrInvokeInstruction(_core.LLVMBuildCall(self.ptr, fn.ptr, arg_ptrs, name))
        
    def select(self, cond, then_value, else_value, name=""):
        check_is_value(cond)
        check_is_value(then_value)
        check_is_value(else_value)
        return Value(_core.LLVMBuildSelect(self.ptr, cond.ptr, then_value.ptr, else_value.ptr, name))
    
    def vaarg(self, list_val, ty, name=""):
        check_is_value(list_val)
        check_is_type(ty)
        return Instruction(_core.LLVMBuildVAArg(self.ptr, list_val.ptr, ty.ptr, name))
    
    def extract_element(self, vec_val, idx_val, name=""):
        check_is_value(vec_val)
        check_is_value(idx_val)
        return Value(_core.LLVMBuildExtractElement(self.ptr, vec_val.ptr, idx_val.ptr, name))
    
    def insert_element(self, vec_val, elt_val, idx_val, name=""):
        check_is_value(vec_val)
        check_is_value(elt_val)
        check_is_value(idx_val)
        return Value(_core.LLVMBuildInsertElement(self.ptr, vec_val.ptr, elt_val.ptr, idx_val.ptr, name))

    def shuffle_vector(self, vecA, vecB, mask, name=""):
        check_is_value(vecA)
        check_is_value(vecB)
        check_is_value(mask)
        return Value(_core.LLVMBuildShuffleVector(self.ptr, vecA.ptr, vecB.ptr, mask.ptr, name))


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

