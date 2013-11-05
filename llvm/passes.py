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
from llvmpy import api

#===----------------------------------------------------------------------===
# Pass manager builder
#===----------------------------------------------------------------------===

class PassManagerBuilder(llvm.Wrapper):
    @staticmethod
    def new():
        return PassManagerBuilder(api.llvm.PassManagerBuilder.new())

    def populate(self, pm):
        if isinstance(pm, FunctionPassManager):
            self._ptr.populateFunctionPassManager(pm._ptr)
        else:
            self._ptr.populateModulePassManager(pm._ptr)

    @property
    def opt_level(self):
        return self._ptr.OptLevel

    @opt_level.setter
    def opt_level(self, optlevel):
        self._ptr.OptLevel = optlevel

    @property
    def size_level(self):
        return self._ptr.SizeLevel

    @size_level.setter
    def size_level(self, sizelevel):
        self._ptr.SizeLevel = sizelevel

    if llvm.version >= (3, 3):
        @property
        def bbvectorize(self):
            return self._ptr.BBVectorize

        @bbvectorize.setter
        def bbvectorize(self, enable):
            self._ptr.BBVectorize = enable

        vectorize = bbvectorize

        @property
        def slpvectorize(self):
            return self._ptr.SLPVectorize

        @slpvectorize.setter
        def slpvectorize(self, enable):
            self._ptr.SLPVectorize = enable

    else:
        @property
        def vectorize(self):
            return self._ptr.Vectorize

        @vectorize.setter
        def vectorize(self, enable):
            self._ptr.Vectorize = enable


    @property
    def loop_vectorize(self):
        try:
            return self._ptr.LoopVectorize
        except AttributeError:
            return False

    @loop_vectorize.setter
    def loop_vectorize(self, enable):
        if llvm.version >= (3, 2):
            self._ptr.LoopVectorize = enable
        elif enable:
            warnings.warn("Ignored. LLVM-3.1 & prior do not support loop vectorizer.")

    @property
    def disable_unit_at_a_time(self):
        return self._ptr.DisableUnitAtATime

    @disable_unit_at_a_time.setter
    def disable_unit_at_a_time(self, disable):
        self._ptr.DisableUnitAtATime = disable

    @property
    def disable_unroll_loops(self):
        return self._ptr.DisableUnrollLoops

    @disable_unroll_loops.setter
    def disable_unroll_loops(self, disable):
        self._ptr.DisableUnrollLoops = disable

    if llvm.version <= (3, 3):
        @property
        def disable_simplify_lib_calls(self):
            return self._ptr.DisableSimplifyLibCalls

        @disable_simplify_lib_calls.setter
        def disable_simplify_lib_calls(self, disable):
            self._ptr.DisableSimplifyLibCalls = disable

    def use_inliner_with_threshold(self, threshold):
        self._ptr.Inliner = api.llvm.createFunctionInliningPass(threshold)


#===----------------------------------------------------------------------===
# Pass manager
#===----------------------------------------------------------------------===

class PassManager(llvm.Wrapper):

    @staticmethod
    def new():
        return PassManager(api.llvm.PassManager.new())

    def add(self, pass_obj):
        '''Add a pass to the pass manager.

        pass_obj --- Either a Pass instance, a string name of a pass
        '''
        if isinstance(pass_obj, Pass):
            self._ptr.add(pass_obj._ptr)
        else:
            self._add_pass(str(pass_obj))

    def _add_pass(self, pass_name):
        passreg = api.llvm.PassRegistry.getPassRegistry()
        a_pass = passreg.getPassInfo(pass_name).createPass()
        if not a_pass:
            assert pass_name not in PASSES, "Registered but not found?"
            raise llvm.LLVMException('Invalid pass name "%s"' % pass_name)
        self._ptr.add(a_pass)

    def run(self, module):
        return self._ptr.run(module._ptr)

class FunctionPassManager(PassManager):

    @staticmethod
    def new(module):
        ptr = api.llvm.FunctionPassManager.new(module._ptr)
        return FunctionPassManager(ptr)

    def __init__(self, ptr):
        PassManager.__init__(self, ptr)

    def initialize(self):
        self._ptr.doInitialization()

    def run(self, fn):
        return self._ptr.run(fn._ptr)

    def finalize(self):
        self._ptr.doFinalization()

#===----------------------------------------------------------------------===
# Passes
#===----------------------------------------------------------------------===

class Pass(llvm.Wrapper):
    '''Pass Inferface
        '''

    @staticmethod
    def new(name):
        '''Create a new pass by name.

            Note: Not all pass has a default constructor.  LLVM will kill
            the process if an the pass requires arguments to construct.
            The error cannot be caught.
            '''
        passreg = api.llvm.PassRegistry.getPassRegistry()
        a_pass = passreg.getPassInfo(name).createPass()
        p = Pass(a_pass)
        p.__name = name
        return p

    @property
    def name(self):
        '''The name used in PassRegistry.
        '''
        try:
            return self.__name
        except AttributeError:
            return

    @property
    def description(self):
        return self._ptr.getPassName()

    def dump(self):
        return self._ptr.dump()

#===----------------------------------------------------------------------===
# Target data
#===----------------------------------------------------------------------===

class TargetData(Pass):

    @staticmethod
    def new(strrep):
        ptr = api.llvm.DataLayout.new(strrep)
        return TargetData(ptr)

    def clone(self):
        return TargetData.new(str(self))

    def __str__(self):
        return self._ptr.getStringRepresentation()

    @property
    def byte_order(self):
        if self._ptr.isLittleEndian():
            return 1
        else:
            return 0

    @property
    def pointer_size(self):
        return self._ptr.getPointerSize()

    @property
    def target_integer_type(self):
        context = api.llvm.getGlobalContext()
        return api.llvm.IntegerType(api.llvm.Type.getInt32Ty(context))

    def size(self, ty):
        return self._ptr.getTypeSizeInBits(ty._ptr)

    def store_size(self, ty):
        return self._ptr.getTypeStoreSize(ty._ptr)

    def abi_size(self, ty):
        return self._ptr.getTypeAllocSize(ty._ptr)

    def abi_alignment(self, ty):
        return self._ptr.getABITypeAlignment(ty._ptr)

    def callframe_alignment(self, ty):
        return self._ptr.getCallFrameTypeAlignment(ty._ptr)

    def preferred_alignment(self, ty_or_gv):
        if isinstance(ty_or_gv, core.Type):
            return self._ptr.getPrefTypeAlignment(ty_or_gv._ptr)
        elif isinstance(ty_or_gv, core.GlobalVariable):
            return self._ptr.getPreferredAlignment(ty_or_gv._ptr)
        else:
            raise core.LLVMException("argument is neither a type nor a global variable")

    def element_at_offset(self, ty, ofs):
        return self._ptr.getStructLayout(ty._ptr).getElementContainingOffset(ofs)

    def offset_of_element(self, ty, el):
        return self._ptr.getStructLayout(ty._ptr).getElementOffset(el)

#===----------------------------------------------------------------------===
# Target Library Info
#===----------------------------------------------------------------------===

class TargetLibraryInfo(Pass):
    @staticmethod
    def new(triple):
        triple = api.llvm.Triple.new(str(triple))
        ptr = api.llvm.TargetLibraryInfo.new(triple)
        return TargetLibraryInfo(ptr)

#===----------------------------------------------------------------------===
# Target Transformation Info
#===----------------------------------------------------------------------===

class TargetTransformInfo(Pass):
    @staticmethod
    def new(targetmachine):
        scalartti = targetmachine._ptr.getScalarTargetTransformInfo()
        vectortti = targetmachine._ptr.getVectorTargetTransformInfo()
        ptr = api.llvm.TargetTransformInfo.new(scalartti, vectortti)
        return TargetTransformInfo(ptr)


#===----------------------------------------------------------------------===
# Helpers
#===----------------------------------------------------------------------===

def build_pass_managers(tm, opt=2, loop_vectorize=False, slp_vectorize=False,
                        vectorize=False, inline_threshold=None,
                        pm=True, fpm=True, mod=None):
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
    if inline_threshold is None:
        if opt == 1:
            inline_threshold = 75
        elif opt == 2:
            inline_threshold = 25
        else:
            inline_threshold = 275

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
    if llvm.version >= (3, 3):
        pmb.slp_vectorize = slp_vectorize
    if inline_threshold:
        pmb.use_inliner_with_threshold(inline_threshold)
    if pm:
        pm.add(tm.target_data.clone())
        pm.add(TargetLibraryInfo.new(tm.triple))
        if llvm.version <= (3, 2):
            pm.add(TargetTransformInfo.new(tm))
        else:
            tm.add_analysis_passes(pm)
        pmb.populate(pm)

    if fpm:
        fpm.add(tm.target_data.clone())
        fpm.add(TargetLibraryInfo.new(tm.triple))
        if llvm.version <= (3, 2):
            fpm.add(TargetTransformInfo.new(tm))
        else:
            tm.add_analysis_passes(pm)
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
    passreg = api.llvm.PassRegistry.getPassRegistry()
    for name, desc in passreg.enumerate():
        yield name, desc

def _initialize_passes():
    global PASSES

    passreg = api.llvm.PassRegistry.getPassRegistry()

    api.llvm.initializeCore(passreg)
    api.llvm.initializeScalarOpts(passreg)
    api.llvm.initializeVectorization(passreg)
    api.llvm.initializeIPO(passreg)
    api.llvm.initializeAnalysis(passreg)
    api.llvm.initializeIPA(passreg)
    api.llvm.initializeTransformUtils(passreg)
    api.llvm.initializeInstCombine(passreg)
    api.llvm.initializeInstrumentation(passreg)
    api.llvm.initializeTarget(passreg)

    PASSES = dict(_dump_all_passes())

    # build globals
    def transform(name):
        return "PASS_%s" % (name.upper().replace('-', '_'))

    global_symbols = globals()
    for i in PASSES:
        assert i not in global_symbols
        global_symbols[transform(i)] = i

_initialize_passes()

