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

"Execution Engine and related classes."

import sys

import llvm
from llvm import core
from llvm.passes import TargetData, TargetTransformInfo
from llvmpy import api, extra

#===----------------------------------------------------------------------===
# import items which were moved to target module
#===----------------------------------------------------------------------===
from llvm.target import (initialize_all, initialize_target,
    print_registered_targets, get_host_cpu_name, get_default_triple,
    TargetMachine,
    BO_BIG_ENDIAN, BO_LITTLE_ENDIAN,
    CM_DEFAULT, CM_JITDEFAULT, CM_SMALL, CM_KERNEL, CM_MEDIUM, CM_LARGE,
    RELOC_DEFAULT, RELOC_STATIC, RELOC_PIC, RELOC_DYNAMIC_NO_PIC)


#===----------------------------------------------------------------------===
# Generic value
#===----------------------------------------------------------------------===

class GenericValue(llvm.Wrapper):

    @staticmethod
    def int(ty, intval):
        ptr = api.llvm.GenericValue.CreateInt(ty._ptr, int(intval), False)
        return GenericValue(ptr)

    @staticmethod
    def int_signed(ty, intval):
        ptr = api.llvm.GenericValue.CreateInt(ty._ptr, int(intval), True)
        return GenericValue(ptr)

    @staticmethod
    def real(ty, floatval):
        if str(ty) == 'float':
            ptr = api.llvm.GenericValue.CreateFloat(float(floatval))
        elif str(ty) == 'double':
            ptr = api.llvm.GenericValue.CreateDouble(float(floatval))
        else:
            raise Exception('Unreachable')
        return GenericValue(ptr)

    @staticmethod
    def pointer(addr):
        '''
        One argument version takes (addr).
        Two argument version takes (ty, addr). [Deprecated]

        `ty` is unused.
        `addr` is an integer representing an address.

        '''
        ptr = api.llvm.GenericValue.CreatePointer(int(addr))
        return GenericValue(ptr)

    def as_int(self):
        return self._ptr.toUnsignedInt()

    def as_int_signed(self):
        return self._ptr.toSignedInt()

    def as_real(self, ty):
        return self._ptr.toFloat(ty._ptr)

    def as_pointer(self):
        return self._ptr.toPointer()

#===----------------------------------------------------------------------===
# Engine builder
#===----------------------------------------------------------------------===

class EngineBuilder(llvm.Wrapper):
    @staticmethod
    def new(module):
        ptr = api.llvm.EngineBuilder.new(module._ptr)
        return EngineBuilder(ptr)

    def force_jit(self):
        self._ptr.setEngineKind(api.llvm.EngineKind.Kind.JIT)
        return self

    def force_interpreter(self):
        self._ptr.setEngineKind(api.llvm.EngineKind.Kind.Interpreter)
        return self

    def opt(self, level):
        '''
        level valid [0, 1, 2, 3] -- [None, Less, Default, Aggressive]
        '''
        assert 0 <= level <= 3
        self._ptr.setOptLevel(level)
        return self

    def mattrs(self, string):
        '''set machine attributes as a comma/space separated string

        e.g: +sse,-3dnow
        '''
        self._ptr.setMAttrs(string.split(','))
        return self

    def create(self, tm=None):
        '''
        tm --- Optional. Provide a TargetMachine.  Ownership is transfered
        to the returned execution engine.
        '''
        if tm is not None:
            engine = self._ptr.create(tm._ptr)
        elif (sys.platform.startswith('win32') and
                    getattr(self, '_use_mcjit', False)):
            # force ELF generation on MCJIT on win32
            triple = get_default_triple()
            tm = TargetMachine.new('%s-elf' % triple)
            engine = self._ptr.create(tm._ptr)
        else:
            engine = self._ptr.create()
        ee = ExecutionEngine(engine)
        ee.finalize_object()                # no effect for legacy JIT
        return ee

    def select_target(self, *args):
        '''get the corresponding target machine

        Accept no arguments or (triple, march, mcpu, mattrs)
        '''
        if args:
            triple, march, mcpu, mattrs = args
            ptr = self._ptr.selectTarget(triple, march, mcpu,
                                          mattrs.split(','))
        else:
            ptr = self._ptr.selectTarget()
        return TargetMachine(ptr)

    def mcjit(self, enable):
        '''Enable/disable MCJIT
        '''
        self._ptr.setUseMCJIT(enable)
        self._use_mcjit = True
        return self

#===----------------------------------------------------------------------===
# Execution engine
#===----------------------------------------------------------------------===

class ExecutionEngine(llvm.Wrapper):

    @staticmethod
    def new(module, force_interpreter=False):
        eb = EngineBuilder.new(module)
        if force_interpreter:
            eb.force_interpreter()
        return eb.create()

    def disable_lazy_compilation(self, disabled=True):
        self._ptr.DisableLazyCompilation(disabled)

    def run_function(self, fn, args):
        ptr = self._ptr.runFunction(fn._ptr, list(map(lambda x: x._ptr, args)))
        return GenericValue(ptr)

    def get_pointer_to_named_function(self, name, abort=True):
        return self._ptr.getPointerToNamedFunction(name, abort)

    def get_pointer_to_function(self, fn):
        return self._ptr.getPointerToFunction(fn._ptr)

    def get_pointer_to_global(self, val):
        return self._ptr.getPointerToGlobal(val._ptr)

    def add_global_mapping(self, gvar, addr):
        assert addr >= 0, "Address cannot not be negative"
        self._ptr.addGlobalMapping(gvar._ptr, addr)

    def run_static_ctors(self):
        self._ptr.runStaticConstructorsDestructors(False)

    def run_static_dtors(self):
        self._ptr.runStaticConstructorsDestructors(True)

    def free_machine_code_for(self, fn):
        self._ptr.freeMachineCodeForFunction(fn._ptr)

    def add_module(self, module):
        self._ptr.addModule(module._ptr)

    def remove_module(self, module):
        return self._ptr.removeModule(module._ptr)

    def finalize_object(self):
        return self._ptr.finalizeObject()

    @property
    def target_data(self):
        ptr = self._ptr.getDataLayout()
        return TargetData(ptr)


#===----------------------------------------------------------------------===
# Dynamic Library
#===----------------------------------------------------------------------===

def dylib_add_symbol(name, ptr):
    api.llvm.sys.DynamicLibrary.AddSymbol(name, ptr)

def dylib_address_of_symbol(name):
    return api.llvm.sys.DynamicLibrary.SearchForAddressOfSymbol(name)
