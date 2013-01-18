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

"""Pass managers and passes.

This module provides the LLVM pass managers and the passes themselves.
All transformation passes listed at http://www.llvm.org/docs/Passes.html
are available.
"""

import llvm                 # top-level, for common stuff
import llvm.core as core    # module, function etc.
import llvm._core as _core  # C wrappers
import llvm._util as _util  # Utility functions

import warnings
#===----------------------------------------------------------------------===
# Pass manager builder
#===----------------------------------------------------------------------===

class PassManagerBuilder(object):
    @staticmethod
    def new():
        return PassManagerBuilder(_core.LLVMPassManagerBuilderCreate())

    def __init__(self, ptr):
        self.ptr = ptr

    def __del__(self):
        _core.LLVMPassManagerBuilderDispose(self.ptr)

    def populate(self, pm):
        if isinstance(pm, FunctionPassManager):
            return _core.LLVMPassManagerBuilderPopulateFunctionPassManager(
                        self.ptr, pm.ptr)
        else:
            return _core.LLVMPassManagerBuilderPopulateModulePassManager(
                        self.ptr, pm.ptr)


    def _set_opt_level(self, optlevel):
        _core.LLVMPassManagerBuilderSetOptLevel(self.ptr, optlevel)

    def _get_opt_level(self):
        return _core.LLVMPassManagerBuilderGetOptLevel(self.ptr)

    opt_level = property(_get_opt_level, _set_opt_level)

    def _set_size_level(self, sizelevel):
        _core.LLVMPassManagerBuilderSetSizeLevel(self.ptr, sizelevel)

    def _get_size_level(self):
        return _core.LLVMPassManagerBuilderGetSizeLevel(self.ptr)

    size_level = property(_get_size_level, _set_size_level)

    def _set_vectorize(self, enable):
        _core.LLVMPassManagerBuilderSetVectorize(self.ptr, int(bool(enable)))

    def _get_vectorize(self):
        return bool(_core.LLVMPassManagerBuilderGetVectorize(self.ptr))

    vectorize = property(_get_vectorize, _set_vectorize)

    def _set_loop_vectorize(self, enable):
        if llvm.version >= (3, 2):
            _core.LLVMPassManagerBuilderSetLoopVectorize(self.ptr,
                                                         int(bool(enable)))
        elif enable:
            warnings.warn("Ignored. LLVM-3.1 & prior do not support loop vectorizer.")

    def _get_loop_vectorize(self):
        try:
            return bool(_core.LLVMPassManagerBuilderGetLoopVectorize(self.ptr))
        except AttributeError:
            return False

    loop_vectorize = property(_get_loop_vectorize, _set_loop_vectorize)

    def _set_disable_unit_at_a_time(self, disable):
        return _core.LLVMPassManagerBuilderSetDisableUnitAtATime(
                    self.ptr, disable)

    def _get_disable_unit_at_a_time(self):
        return _core.LLVMPassManagerBuilderGetDisableUnitAtATime(
                    self.ptr)

    disable_unit_at_a_time = property(_get_disable_unit_at_a_time,
                                      _set_disable_unit_at_a_time)

    def _set_disable_unroll_loops(self, disable):
        return _core.LLVMPassManagerBuilderGetDisableUnrollLoops(
                    self.ptr, disable)

    def _get_disable_unroll_loops(self):
        return _core.LLVMPassManagerBuilderGetDisableUnrollLoops(self.ptr)

    disable_unroll_loops = property(_get_disable_unroll_loops,
                                    _set_disable_unroll_loops)

    def _set_disable_simplify_lib_calls(self, disable):
        return _core.LLVMPassManagerBuilderGetDisableSimplifyLibCalls(
                    self.ptr, disable)

    def _get_disable_simplify_lib_calls(self):
        return _core.LLVMPassManagerBuilderGetDisableSimplifyLibCalls(self.ptr)

    disable_simplify_lib_calls = property(_get_disable_simplify_lib_calls,
                                          _set_disable_simplify_lib_calls)

    def use_inliner_with_threshold(self, threshold):
        _core.LLVMPassManagerBuilderUseInlinerWithThreshold(self.ptr, threshold)

#===----------------------------------------------------------------------===
# Pass manager
#===----------------------------------------------------------------------===

class PassManager(object):

    @staticmethod
    def new():
        return PassManager(_core.LLVMCreatePassManager())

    def __init__(self, ptr):
        self.ptr = ptr

    def __del__(self):
        _core.LLVMDisposePassManager(self.ptr)

    def add(self, pass_obj):
        '''Add a pass to the pass manager.
        
        pass_obj --- Either a Pass instance, a string name of a pass
        '''
        if isinstance(pass_obj, Pass):
            _util.check_is_unowned(pass_obj)
            _core.LLVMAddPass(self.ptr, pass_obj.ptr)
            pass_obj._own(self) # PassManager owns the pass
        elif _util.isstring(pass_obj):
            self._add_pass(pass_obj)
        else:
            raise llvm.LLVMException("invalid pass_id (%s)" % pass_obj)

    def _add_pass(self, pass_name):
        status = _core.LLVMAddPassByName(self.ptr, pass_name)
        if not status:
            assert pass_name not in PASSES, "Registered but not found?"
            raise llvm.LLVMException('Invalid pass name "%s"' % pass_name)

    def run(self, module):
        core.check_is_module(module)
        return _core.LLVMRunPassManager(self.ptr, module.ptr)

class FunctionPassManager(PassManager):

    @staticmethod
    def new(module):
        core.check_is_module(module)
        ptr = _core.LLVMCreateFunctionPassManagerForModule(module.ptr)
        return FunctionPassManager(ptr)

    def __init__(self, ptr):
        PassManager.__init__(self, ptr)

    def initialize(self):
        _core.LLVMInitializeFunctionPassManager(self.ptr)

    def run(self, fn):
        core.check_is_function(fn)
        return _core.LLVMRunFunctionPassManager(self.ptr, fn.ptr)

    def finalize(self):
        _core.LLVMFinalizeFunctionPassManager(self.ptr)



#===----------------------------------------------------------------------===
# Passes
#===----------------------------------------------------------------------===

class Pass(llvm.Ownable):
    '''Pass Inferface
    '''
    def __init__(self, ptr):
        llvm.Ownable.__init__(self, ptr, _core.LLVMDisposePass)
        self.__name = ''

    @staticmethod
    def new(name):
        '''Create a new pass by name.

        Note: Not all pass has a default constructor.  LLVM will kill
        the process if an the pass requires arguments to construct.
        The error cannot be caught.
        '''
        ptr = _core.LLVMCreatePassByName(name)
        p = Pass(ptr)
        p.__name = name
        return p

    @property
    def name(self):
        '''The name used in PassRegistry.
        '''
        return self.__name

    @property
    def description(self):
        return _core.LLVMGetPassName(self.ptr)

    def dump(self):
        return _core.LLVMPassDump(self.ptr)


#===----------------------------------------------------------------------===
# Target data
#===----------------------------------------------------------------------===

class TargetData(Pass):

    @staticmethod
    def new(strrep):
        return TargetData(_core.LLVMCreateTargetData(strrep))

    def clone(self):
        return TargetData.new(str(self))

    def __str__(self):
        return _core.LLVMTargetDataAsString(self.ptr)

    @property
    def byte_order(self):
        return _core.LLVMByteOrder(self.ptr)

    @property
    def pointer_size(self):
        return _core.LLVMPointerSize(self.ptr)

    @property
    def target_integer_type(self):
        ptr = _core.LLVMIntPtrType(self.ptr);
        return core.IntegerType(ptr, core.TYPE_INTEGER)

    def size(self, ty):
        core.check_is_type(ty)
        return _core.LLVMSizeOfTypeInBits(self.ptr, ty.ptr)

    def store_size(self, ty):
        core.check_is_type(ty)
        return _core.LLVMStoreSizeOfType(self.ptr, ty.ptr)

    def abi_size(self, ty):
        core.check_is_type(ty)
        return _core.LLVMABISizeOfType(self.ptr, ty.ptr)

    def abi_alignment(self, ty):
        core.check_is_type(ty)
        return _core.LLVMABIAlignmentOfType(self.ptr, ty.ptr)

    def callframe_alignment(self, ty):
        core.check_is_type(ty)
        return _core.LLVMCallFrameAlignmentOfType(self.ptr, ty.ptr)

    def preferred_alignment(self, ty_or_gv):
        if isinstance(ty_or_gv, core.Type):
            return _core.LLVMPreferredAlignmentOfType(self.ptr,
                                                      ty_or_gv.ptr)
        elif isinstance(ty_or_gv, core.GlobalVariable):
            return _core.LLVMPreferredAlignmentOfGlobal(self.ptr,
                                                        ty_or_gv.ptr)
        else:
            raise core.LLVMException("argument is neither a type nor a global variable")

    def element_at_offset(self, ty, ofs):
        core.check_is_type_struct(ty)
        ofs = int(ofs) # ofs is unsigned long long
        return _core.LLVMElementAtOffset(self.ptr, ty.ptr, ofs)

    def offset_of_element(self, ty, el):
        core.check_is_type_struct(ty)
        el = int(el) # el should be an int
        return _core.LLVMOffsetOfElement(self.ptr, ty.ptr, el)


#===----------------------------------------------------------------------===
# Target Library Info
#===----------------------------------------------------------------------===

class TargetLibraryInfo(Pass):
    @staticmethod
    def new(triple):
        ptr = _core.LLVMCreateTargetLibraryInfo(triple)
        return TargetLibraryInfo(ptr)


#===----------------------------------------------------------------------===
# Target Transform Info
#===----------------------------------------------------------------------===

class TargetTransformInfo(Pass):
    @staticmethod
    def new(targetmachine):
        llvm.require_version_at_least(3, 2)
        ptr = _core.LLVMCreateTargetTransformInfo(targetmachine.ptr)
        return TargetTransformInfo(ptr)


#===----------------------------------------------------------------------===
# Helpers
#===----------------------------------------------------------------------===

def build_pass_managers(tm, opt=2, loop_vectorize=False, vectorize=False,
                        inline_threshold=2000, pm=True, fpm=True, mod=None):
    '''
    tm --- The TargetMachine for which the passes are optimizing for.
           The TargetMachine must stay alive until the pass managers 
           are removed.
    opt --- [0-3] Optimization level. Default to 2.
    loop_vectorize --- [boolean] Whether to use loop-vectorizer.
    vectorize --- [boolean] Whether to use basic-block vectorizer.
    inline_threshold --- [int] Threshold for the inliner.
    features --- [str] CPU feature string.
    pm --- [boolean] Whether to build a module-level pass-manager.
    fpm --- [boolean] Whether to build a function-level pass-manager.
    mod --- [Module] The module object for the FunctionPassManager.
    '''
    if pm:
        pm = PassManager.new()
    if fpm:
        if not mod:
            raise TypeError("Keyword 'mod' must be defined")
        fpm = FunctionPassManager.new(mod)

    # Populate PassManagers with target specific passes
    pmb = PassManagerBuilder.new()
    pmb.opt_level = opt
    pmb.vectorize = vectorize
    pmb.loop_vectorize = loop_vectorize
    if inline_threshold:
        pmb.use_inliner_with_threshold(inline_threshold)
    if pm:
        pm.add(tm.target_data.clone())
        pm.add(TargetLibraryInfo.new(tm.triple))
        if llvm.version >= (3, 2):
            pm.add(TargetTransformInfo.new(tm))
        pmb.populate(pm)

    if fpm:
        fpm.add(tm.target_data)
        fpm.add(TargetLibraryInfo.new(tm.triple))
        if llvm.version >= (3, 2):
            fpm.add(TargetTransformInfo.new(tm))
        pmb.populate(fpm)
        fpm.initialize()

    from collections import namedtuple
    return namedtuple('passmanagers', ['pm', 'fpm'])(pm=pm, fpm=fpm)


#===----------------------------------------------------------------------===
# Misc.
#===----------------------------------------------------------------------===

# Intialize passes
PASSES = None

def _dump_all_passes():
    passes_sep_by_line = _core.LLVMDumpPasses()
    strip = lambda S : S.strip()
    for line in passes_sep_by_line.splitlines():
        passarg, passname = map(strip, line.split('\t', 1))
        if passarg:
            yield passarg, passname

def _initialize_passes():
    global PASSES
    _core.LLVMInitializePasses()
    PASSES = dict(_dump_all_passes())

    # build globals
    def transform(name):
        return "PASS_%s" % (name.upper().replace('-', '_'))

    global_symbols = globals()
    for i in PASSES:
        assert i not in global_symbols
        global_symbols[transform(i)] = i

_initialize_passes()

