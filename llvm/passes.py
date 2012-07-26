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
import llvm.ee as ee        # target data
import llvm.core as core    # module, function etc.
import llvm._core as _core  # C wrappers
import llvm._util as _util  # Utility functions

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

    def add(self, tgt_data_or_pass_name):
        if isinstance(tgt_data_or_pass_name, ee.TargetData):
            self._add_target_data(tgt_data_or_pass_name)
        elif _util.isstring(tgt_data_or_pass_name):
            self._add_pass(tgt_data_or_pass_name)
        else:
            raise llvm.LLVMException("invalid pass_id (%s)" % tgt_data_or_pass_name)

    def _add_target_data(self, tgt):
        _core.LLVMAddTargetData(tgt.ptr, self.ptr)

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

