#!/usr/bin/env python
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

import sys, os
import os.path
from distutils.core import setup, Extension

LLVM_PY_VERSION = '0.7'


def get_libs_and_objs(llvm_lib_dir):
    # Libraries that are not included in the build
    not_required_libs = """
BrainF
bugpoint
Fibonacci
HowToUseJIT
Kaleidoscope
llc
lli
llvm-as
llvm-bcanalyzer
llvm-extract
llvm-ld
llvm-link
llvm-mc
LLVMArchive
LLVMAsmPrinter
LLVMHello
LLVMDebugger
llvm_headers_do_not_build
ModuleMaker
opt
tblgen
"""
    libs = """
LLVMAnalysis
LLVMAsmParser
LLVMAsmPrinter
LLVMBitReader
LLVMBitWriter
LLVMCodeGen
LLVMCore
LLVMExecutionEngine
LLVMInstCombine
LLVMInstrumentation
LLVMInterpreter
LLVMipa
LLVMipo
LLVMJIT
LLVMLinker
LLVMMC
LLVMMCParser
LLVMScalarOpts
LLVMSelectionDAG
LLVMSupport
LLVMTarget
LLVMTransformUtils
LLVMVectorize
LLVMX86AsmParser
LLVMX86AsmPrinter
LLVMX86CodeGen
LLVMX86Desc
LLVMX86Info
LLVMX86Utils
Advapi32
Shell32
""".split()
    return (libs, [])


def get_llvm_config():

    # get from command-line, or use default
    llvm_dir = r'C:\Program Files\LLVM 3.1.1'
    i = 0
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg.startswith('--llvm-dir='):
            del sys.argv[i]
            llvm_dir = arg.split('=')[1]
        else:
            i += 1
    good = os.path.isdir( llvm_dir )
    return (llvm_dir, good)


def call_setup(llvm_dir):
    incdirs = [os.path.join(llvm_dir, 'include')]
    libdir = os.path.join(llvm_dir, 'lib')

    libs_core, objs_core = get_libs_and_objs(libdir)
    std_libs = []

    ext_core = Extension(
        'llvm._core',
        ['llvm/_core.cpp', 'llvm/wrap.cpp', 'llvm/extra.cpp'],
        include_dirs = incdirs,
        library_dirs = [libdir],
        libraries = std_libs + libs_core,
        language = 'c++' )

    setup(
        name='llvm-py',
        version=LLVM_PY_VERSION,
        description='Python Bindings for LLVM',
        author='Mahadevan R',
        author_email='mdevan@mdevan.org',
        url='http://www.mdevan.org/llvm-py/',
        packages=['llvm'],
        py_modules = [ 'llvm.core' ],
        ext_modules = [ ext_core ],)


def main():

    # get llvm config
    llvm_dir, is_good = get_llvm_config()
    print("Using llvm-dir=" + llvm_dir)
    if not is_good:
        print("Cannot find llvm-dir")
        print("Try again with --llvm-dir=/path/to/llvm-top-dir.")
        return 1

    # setup
    call_setup(llvm_dir)

    # done
    return 0


ev = main()
sys.exit(ev)
