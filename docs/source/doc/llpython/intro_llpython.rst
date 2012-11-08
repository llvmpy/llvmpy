====================
Introducing LLPython
====================

In this article, we introduce the llpython package.  The primary goal
of the llpython package is to provide a Python dialect/subset that
maps directly to LLVM code.  LLPython differs from its originating
LLVM translator, Numba, in the following aspects:

  * LLPython code is not intended to work in Python if not translated
    and wrapped.
  * The LLPython translator only uses LLVM types.
  * LLPython is explicitly typed, and does not support type inference.
    LLPython does not support implicit casts, all casts must be explicit.
  * LLPython supports code that directly calls the C API, the Python C
    API, and the llvm.core.Builder methods.

Additionally, we designed the sub-package to have the following
engineering properties:

  * Usable from Python 2.7, and 3.X.  At the time of writing, we plan
    to support Python 2.6.
  * Clean from Numba dependencies (other than llvmpy), and can be used
    as a standalone code generator without a full Numba installation.
  * Provides a series of Python bytecode passes that can be easily
    used by other projects.


LLPython Origins
================

We developed LLPython with the initial goal of simplifying writing
LLVM code.


LLPython Internals
==================

In this section, we describe the various passes performed by the
LLPython translator.


Conclusions
===========

LLPython is neat.
