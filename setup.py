#!/usr/bin/env python
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

import sys
import os
import re
from distutils.core import setup, Extension


LLVM_PY_VERSION = '0.8.2'

llvm_config = os.environ('LLVM_CONFIG_PATH', 'llvm-config')

def run_llvm_config(args):
    cmd = llvm_config + ' ' + ' '.join(args)
    return os.popen(cmd).read().rstrip()

if run_llvm_config(['version']) == '':
    print("Cannot invoke llvm-config.")
    print("Try setting LLVM_CONFIG_PATH=/path/to/llvm-config")
    sys.exit(1)


def get_libs_and_objs(components):
    parts = run_llvm_config([' --libs'] + components)
    libs = []
    objs = []
    for part in parts:
        if part.startswith('-l'):
            libs.append(part[2:])
        elif part.endswith('.o'):
            objs.append(part)
    return libs, objs


def get_llvm_version():
    # get version number; treat it as fixed point
    pat = re.compile(r'(\d+)\.(\d+)')
    m = pat.search(run_llvm_config([' --version']))
    if m is None:
        sys.exit('could not determine llvm version')
    return tuple(map(int, m.groups()))


def auto_intrinsic_gen(incdir):
    # let's do auto intrinsic generation
    print("Generate intrinsic IDs")
    from tools import intrgen
    path = "%s/llvm/Intrinsics.gen" % incdir
    with open('llvm/_intrinsic_ids.py', 'w') as fout:
        intrgen.gen(path, fout)


incdir = run_llvm_config(['--includedir'])
libdir = run_llvm_config(['--libdir'])

llvm_version = get_llvm_version()
print('LLVM version = %d.%d' % llvm_version)

auto_intrinsic_gen(incdir)

if llvm_version <= (3, 1): # select between PTX & NVPTX
    print('Using PTX')
    ptx_components = ['ptx',
                      'ptxasmprinter',
                      'ptxcodegen',
                      'ptxdesc',
                      'ptxinfo']
else:
    print('Using NVPTX')
    ptx_components = ['nvptx',
                      'nvptxasmprinter',
                      'nvptxcodegen',
                      'nvptxdesc',
                      'nvptxinfo']

libs_core, objs_core = get_libs_and_objs(
    ['core', 'analysis', 'scalaropts', 'executionengine',
     'jit',  'native', 'interpreter', 'bitreader', 'bitwriter',
     'instrumentation', 'ipa', 'ipo', 'transformutils',
     'asmparser', 'linker', 'support', 'vectorize']
     + ptx_components)

std_libs = ['pthread', 'm', 'stdc++', 'dl']
extra_link_args = ["-fPIC"]
if sys.platform == 'darwin':
    std_libs.append("ffi")

ext_core = Extension(
    name='llvm._core',
    sources=['llvm/_core.cpp', 'llvm/wrap.cpp', 'llvm/extra.cpp'],
    define_macros = [('__STDC_CONSTANT_MACROS', None),
                     ('__STDC_LIMIT_MACROS', None),
                     ('_GNU_SOURCE', None)],
    include_dirs = ['/usr/include', incdir],
    library_dirs = [libdir],
    libraries = std_libs + libs_core,
    extra_objects = objs_core,
    extra_link_args = extra_link_args,
)

setup(
    name = 'llvm-py',
    version = LLVM_PY_VERSION,
    description = 'Python Bindings for LLVM',
    author = 'Mahadevan R',
    author_email = 'mdevan@mdevan.org',
    url = 'http://www.llvmpy.org/',
    packages = ['llvm'],
    py_modules = ['llvm.core'],
    ext_modules = [ ext_core ],
)
