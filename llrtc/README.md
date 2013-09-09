# LLRT: Low Level Runtime

## Why?

The same reason for LLVM compiler-rt.  LLVM generates libgcc symbols, such as
__divdi3 for 64-bit division on 32-bit platform.  They are not also available.
We need to ship compiler-rt but it is not Windows ready.
This subproject aims to provide a small portable subset of compiler-rt.
Start small and add only the things we really needed.
Performance is not crucial but should not be terrible.
Functionality and usefullness should be more important than performance.

## Developer Instructions

LLRT implements some functionalities in compiler-rt in ANSI C.
The C files are compiled using clang to produce LLVM IR which are shipped.
The IR files are committed in the repository.
So, remember to build the IR files commit them after modifying the C files.

## Build Requirement

- Make
- Clang
- Python

