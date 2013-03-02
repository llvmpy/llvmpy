from binding import *
from ..namespace import llvm

from src.Pass import ImmutablePass

TargetLibraryInfo = llvm.Class(ImmutablePass)

LibFunc = llvm.Namespace('LibFunc')
LibFunc.Enum('Func',  '''
                ZdaPv, ZdlPv, Znaj, ZnajRKSt9nothrow_t,
                Znam, ZnamRKSt9nothrow_t, Znwj, ZnwjRKSt9nothrow_t,
                Znwm, ZnwmRKSt9nothrow_t, cxa_atexit, cxa_guard_abort,
                cxa_guard_acquire, cxa_guard_release, memcpy_chk,
                acos, acosf, acosh, acoshf,
                acoshl, acosl, asin, asinf,
                asinh, asinhf, asinhl, asinl,
                atan, atan2, atan2f, atan2l,
                atanf, atanh, atanhf, atanhl,
                atanl, calloc, cbrt, cbrtf,
                cbrtl, ceil, ceilf, ceill,
                copysign, copysignf, copysignl, cos,
                cosf, cosh, coshf, coshl,
                cosl, exp, exp10, exp10f,
                exp10l, exp2, exp2f, exp2l,
                expf, expl, expm1, expm1f,
                expm1l, fabs, fabsf, fabsl,
                fiprintf,
                floor, floorf, floorl, fmod,
                fmodf, fmodl, fputc,
                fputs, free, fwrite, iprintf,
                log, log10, log10f, log10l,
                log1p, log1pf, log1pl, log2,
                log2f, log2l, logb, logbf,
                logbl, logf, logl, malloc,
                memchr, memcmp, memcpy, memmove,
                memset, memset_pattern16, nearbyint, nearbyintf,
                nearbyintl, posix_memalign, pow, powf,
                powl, putchar, puts,
                realloc, reallocf, rint, rintf,
                rintl, round, roundf, roundl,
                sin, sinf, sinh, sinhf,
                sinhl, sinl, siprintf,
                sqrt, sqrtf, sqrtl, stpcpy,
                strcat, strchr, strcmp, strcpy,
                strcspn, strdup, strlen, strncat,
                strncmp, strncpy, strndup, strnlen,
                strpbrk, strrchr, strspn, strstr,
                strtod, strtof, strtol, strtold,
                strtoll, strtoul, strtoull, tan,
                tanf, tanh, tanhf, tanhl,
                tanl, trunc, truncf,
                truncl, valloc, NumLibFuncs''')
                # not in llvm-3.2 abs, ffs, ffsl, ffsll, fprintf, isascii,
                #             isdigit, labs, llabs, printf, sprintf, toascii

from src.ADT.Triple import Triple
from src.ADT.StringRef import StringRef


@TargetLibraryInfo
class TargetLibraryInfo:
    _include_ = 'llvm/Target/TargetLibraryInfo.h'

    new = Constructor()
    new |= Constructor(ref(Triple))

    delete = Destructor()

    has = Method(cast(bool, Bool), LibFunc.Func)
    hasOptimizedCodeGen = Method(cast(bool, Bool), LibFunc.Func)

    getName = Method(cast(str, StringRef), LibFunc.Func)

    setUnavailable = Method(Void, LibFunc.Func)
    setAvailable = Method(Void, LibFunc.Func)
    setAvailableWithName = Method(Void, LibFunc.Func, cast(str, StringRef))
    disableAllFunctions = Method()

