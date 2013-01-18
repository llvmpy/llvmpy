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

"""Execution Engine and related classes.

"""

import llvm                 # top-level, for common stuff
import llvm.core as core    # module, function etc.
import llvm._core as _core  # C wrappers
import llvm._util as _util  # utility functions
import logging
import os

logger = logging.getLogger(__name__)


# re-export TargetData for backward compatibility.
from llvm.passes import TargetData

def _detect_avx_support():
    '''FIXME: This is a workaround for AVX support.
    '''
    disable_avx_detect = int(os.environ.get('LLVMPY_DISABLE_AVX_DETECT', 0))
    if disable_avx_detect:
        return False # enable AVX if user disable AVX detect
    force_disable_avx = int(os.environ.get('LLVMPY_FORCE_DISABLE_AVX', 0))
    if force_disable_avx:
        return True # force disable AVX
    # auto-detect avx
    try:
        for line in open('/proc/cpuinfo'):
            if line.lstrip().startswith('flags') and 'avx' in line.split():
                # enable AVX if flags contain AVX
                return False
    except IOError:
        pass # disable AVX if no /proc/cpuinfo is found
    return True # disable AVX if flags does not have AVX

FORCE_DISABLE_AVX = _detect_avx_support()

#===----------------------------------------------------------------------===
# Enumerations
#===----------------------------------------------------------------------===

BO_BIG_ENDIAN       = 0
BO_LITTLE_ENDIAN    = 1

# CodeModel
CM_DEFAULT = 0
CM_JITDEFAULT = 1
CM_SMALL = 2
CM_KERNEL = 3
CM_MEDIUM = 4
CM_LARGE = 5

#===----------------------------------------------------------------------===
# Generic value
#===----------------------------------------------------------------------===

class GenericValue(object):

    @staticmethod
    def int(ty, intval):
        core.check_is_type(ty)
        ptr = _core.LLVMCreateGenericValueOfInt(ty.ptr, intval, 0)
        return GenericValue(ptr)

    @staticmethod
    def int_signed(ty, intval):
        core.check_is_type(ty)
        ptr = _core.LLVMCreateGenericValueOfInt(ty.ptr, intval, 1)
        return GenericValue(ptr)

    @staticmethod
    def real(ty, floatval):
        core.check_is_type(ty)   # only float or double
        ptr = _core.LLVMCreateGenericValueOfFloat(ty.ptr, floatval)
        return GenericValue(ptr)

    @staticmethod
    def pointer(*args):
        '''
        One argument version takes (addr).
        Two argument version takes (ty, addr). [Deprecated]

        `ty` is unused.
        `addr` is an integer representing an address.

        TODO: remove two argument version.
        '''
        if len(args)==2:
            logger.warning("Deprecated: Two argument version of "
                           "GenericValue.pointer() is deprecated.")
            addr = args[1]
        elif len(args)!=1:
            raise TypeError("pointer() takes 1 or 2 arguments.")
        else:
            addr = args[0]
        ptr = _core.LLVMCreateGenericValueOfPointer(addr)
        return GenericValue(ptr)

    def __init__(self, ptr):
        self.ptr = ptr

    def __del__(self):
        _core.LLVMDisposeGenericValue(self.ptr)

    def as_int(self):
        return _core.LLVMGenericValueToInt(self.ptr, 0)

    def as_int_signed(self):
        return _core.LLVMGenericValueToInt(self.ptr, 1)

    def as_real(self, ty):
        core.check_is_type(ty)   # only float or double
        return _core.LLVMGenericValueToFloat(ty.ptr, self.ptr)

    def as_pointer(self):
        return _core.LLVMGenericValueToPointer(self.ptr)


# helper functions for generic value objects
def check_is_generic_value(obj): _util.check_gen(obj, GenericValue)
def _unpack_generic_values(objlist):
    return _util.unpack_gen(objlist, check_is_generic_value)


#===----------------------------------------------------------------------===
# Engine builder
#===----------------------------------------------------------------------===

class EngineBuilder(object):
    @staticmethod
    def new(module):
        core.check_is_module(module)
        _util.check_is_unowned(module)
        obj = _core.LLVMCreateEngineBuilder(module.ptr)
        return EngineBuilder(obj, module)

    def __init__(self, ptr, module):
        self.ptr = ptr
        self._module = module
        self.__has_mattrs = False

    def __del__(self):
        _core.LLVMDisposeEngineBuilder(self.ptr)

    def force_jit(self):
        _core.LLVMEngineBuilderForceJIT(self.ptr)
        return self

    def force_interpreter(self):
        _core.LLVMEngineBuilderForceInterpreter(self.ptr)
        return self

    def opt(self, level):
        '''
        level valid [0, 1, 2, 3] -- [None, Less, Default, Aggressive]
        '''
        assert level in range(4)
        _core.LLVMEngineBuilderSetOptLevel(self.ptr, level)
        return self

    def mattrs(self, string):
        '''set machine attributes as a comma/space separated string

        e.g: +sse,-3dnow
        '''
        self.__has_mattrs = True
        if FORCE_DISABLE_AVX:
            if 'avx' not in map(lambda x: x.strip(), string.split(',')):
                # User did not override
                string += ',-avx'
        _core.LLVMEngineBuilderSetMAttrs(self.ptr, string.replace(',', ' '))
        return self

    def create(self, tm=None):
        '''
        tm --- Optional. Provide a TargetMachine.  Ownership is transfered
               to the returned execution engine.
        '''
        if not self.__has_mattrs and FORCE_DISABLE_AVX:
            self.mattrs('-avx')

        if tm:
            _util.check_is_unowned(tm)
            ret = _core.LLVMEngineBuilderCreateTM(self.ptr, tm.ptr)
        else:
            ret = _core.LLVMEngineBuilderCreate(self.ptr)
        if isinstance(ret, str):
            raise llvm.LLVMException(ret)
        engine = ExecutionEngine(ret, self._module)
        if tm:
            tm._own(owner=llvm.DummyOwner)
        return engine

    def select_target(self):
        '''get the corresponding target machine
        '''
        ptr = _core.LLVMTargetMachineFromEngineBuilder(self.ptr)
        return TargetMachine(ptr)

#===----------------------------------------------------------------------===
# Execution engine
#===----------------------------------------------------------------------===

class ExecutionEngine(object):

    @staticmethod
    def new(module, force_interpreter=False):
        eb = EngineBuilder.new(module)
        if force_interpreter:
            eb.force_interpreter()
        return eb.create()

    def __init__(self, ptr, module):
        self.ptr = ptr
        module._own(self)

    def __del__(self):
        _core.LLVMDisposeExecutionEngine(self.ptr)

    def disable_lazy_compilation(self, disabled=True):
        _core.LLVMExecutionEngineDisableLazyCompilation(self.ptr,
                                                        int(bool(disabled)))

    def run_function(self, fn, args):
        core.check_is_function(fn)
        ptrs = _unpack_generic_values(args)
        gvptr = _core.LLVMRunFunction2(self.ptr, fn.ptr, ptrs)
        return GenericValue(gvptr)

    def get_pointer_to_function(self, fn):
        core.check_is_function(fn)
        return _core.LLVMGetPointerToFunction(self.ptr,fn.ptr)

    def get_pointer_to_global(self, val):
        core.check_is_global_value(val)
        return _core.LLVMGetPointerToGlobal(self.ptr, val.ptr)

    def add_global_mapping(self, gvar, addr):
        assert addr >= 0, "Address cannot not be negative"
        _core.LLVMAddGlobalMapping(self.ptr, gvar.ptr, addr)

    def run_static_ctors(self):
        _core.LLVMRunStaticConstructors(self.ptr)

    def run_static_dtors(self):
        _core.LLVMRunStaticDestructors(self.ptr)

    def free_machine_code_for(self, fn):
        core.check_is_function(fn)
        _core.LLVMFreeMachineCodeForFunction(self.ptr, fn.ptr)

    def add_module(self, module):
        core.check_is_module(module)
        _core.LLVMAddModule(self.ptr, module.ptr)
        module._own(self)

    def remove_module(self, module):
        core.check_is_module(module)
        if module.owner != self:
            raise llvm.LLVMException("module is not owned by self")
        ret = _core.LLVMRemoveModule2(self.ptr, module.ptr)
        if isinstance(ret, str):
            raise llvm.LLVMException(ret)
        return core.Module(ret)

    @property
    def target_data(self):
        td = TargetData(_core.LLVMGetExecutionEngineTargetData(self.ptr))
        td._own(self)
        return td


#===----------------------------------------------------------------------===
# Target machine
#===----------------------------------------------------------------------===

def print_registered_targets():
    '''
    Note: print directly to stdout
    '''
    _core.LLVMPrintRegisteredTargetsForVersion()

def get_host_cpu_name():
    '''return the string name of the host CPU
    '''
    return _core.LLVMGetHostCPUName()

def get_default_triple():
    '''return the target triple of the host in str-rep
    '''
    return _core.LLVMDefaultTargetTriple()


class TargetMachine(llvm.Ownable):

    @staticmethod
    def new(triple='', cpu='', features='', opt=2, cm=CM_DEFAULT):
        if not triple and not cpu:
            triple = get_default_triple()
            cpu = get_host_cpu_name()
        ptr = _core.LLVMCreateTargetMachine(triple, cpu, features, opt, cm)
        return TargetMachine(ptr)

    @staticmethod
    def lookup(arch, cpu='', features='', opt=2, cm=CM_DEFAULT):
        '''create a targetmachine given an architecture name

        For a list of architectures,
            use: `llc -help`

        For a list of available CPUs,
            use: `llvm-as < /dev/null | llc -march=xyz -mcpu=help`

        For a list of available attributes (features),
            use: `llvm-as < /dev/null | llc -march=xyz -mattr=help`
        '''
        ptr = _core.LLVMTargetMachineLookup(arch, cpu, features, opt, cm)
        return TargetMachine(ptr)

    def __init__(self, ptr):
        llvm.Ownable.__init__(self, ptr, _core.LLVMDisposeTargetMachine)

    def emit_assembly(self, module):
        '''returns byte string of the module as assembly code of the target machine
        '''
        return _core.LLVMTargetMachineEmitFile(self.ptr, module.ptr, True)

    def emit_object(self, module):
        '''returns byte string of the module as native code of the target machine
        '''
        return _core.LLVMTargetMachineEmitFile(self.ptr, module.ptr, False)

    @property
    def target_data(self):
        '''get target data of this machine
        '''
        ptr = _core.LLVMTargetMachineGetTargetData(self.ptr)
        td = TargetData(ptr)
        td._own(self)
        return td

    @property
    def target_name(self):
        return _core.LLVMTargetMachineGetTargetName(self.ptr)

    @property
    def target_short_description(self):
        return _core.LLVMTargetMachineGetTargetShortDescription(self.ptr)

    @property
    def triple(self):
        return _core.LLVMTargetMachineGetTriple(self.ptr)

    @property
    def cpu(self):
        return _core.LLVMTargetMachineGetCPU(self.ptr)

    @property
    def feature_string(self):
        return _core.LLVMTargetMachineGetFS(self.ptr)

