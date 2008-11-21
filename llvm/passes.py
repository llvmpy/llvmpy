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

"""Pass managers and passes.

This module provides the LLVM pass managers and the passes themselves.
All transformation passes listed at http://www.llvm.org/docs/Passes.html
are available.
"""

import llvm                 # top-level, for common stuff
import llvm.ee as ee        # target data
import llvm.core as core    # module provider, function etc.
import llvm._core as _core  # C wrappers
from llvm._util import *    # utility functions


# passes
PASS_AGGRESSIVE_DCE             = 1
PASS_ARGUMENT_PROMOTION         = 2
PASS_BLOCK_PLACEMENT            = 3
PASS_BREAK_CRITICAL_EDGES       = 4
PASS_CODE_GEN_PREPARE           = 5
PASS_COND_PROPAGATION           = 6
PASS_CONSTANT_MERGE             = 7
PASS_CONSTANT_PROPAGATION       = 8
PASS_DEAD_CODE_ELIMINATION      = 9
PASS_DEAD_ARG_ELIMINATION       = 10
PASS_DEAD_TYPE_ELIMINATION      = 11
PASS_DEAD_INST_ELIMINATION      = 12
PASS_DEAD_STORE_ELIMINATION     = 13
# PASS_GCSE                       = 14: removed in LLVM 2.4
PASS_GLOBAL_DCE                 = 15
PASS_GLOBAL_OPTIMIZER           = 16
PASS_GVN                        = 17
PASS_GVNPRE                     = 18
PASS_IND_MEM_REM                = 19
PASS_IND_VAR_SIMPLIFY           = 20
PASS_FUNCTION_INLINING          = 21
PASS_BLOCK_PROFILER             = 22
PASS_EDGE_PROFILER              = 23
PASS_FUNCTION_PROFILER          = 24
PASS_NULL_PROFILER_RS           = 25
PASS_RS_PROFILING               = 26
PASS_INSTRUCTION_COMBINING      = 27
PASS_INTERNALIZE                = 28
PASS_IP_CONSTANT_PROPAGATION    = 29
PASS_IPSCCP                     = 30
PASS_JUMP_THREADING             = 31
PASS_LCSSA                      = 32
PASS_LICM                       = 33
PASS_LOOP_DELETION              = 34
PASS_LOOP_EXTRACTOR             = 35
PASS_SINGLE_LOOP_EXTRACTOR      = 36
PASS_LOOP_INDEX_SPLIT           = 37
PASS_LOOP_STRENGTH_REDUCE       = 38
PASS_LOOP_ROTATE                = 39
PASS_LOOP_UNROLL                = 40
PASS_LOOP_UNSWITCH              = 41
PASS_LOOP_SIMPLIFY              = 42
PASS_LOWER_ALLOCATIONS          = 43
PASS_LOWER_INVOKE               = 44
PASS_LOWER_SET_JMP              = 45
PASS_LOWER_SWITCH               = 46
PASS_PROMOTE_MEMORY_TO_REGISTER = 47
PASS_MEM_CPY_OPT                = 48
PASS_UNIFY_FUNCTION_EXIT_NODES  = 49
PASS_PREDICATE_SIMPLIFIER       = 50
PASS_PRUNE_EH                   = 51
PASS_RAISE_ALLOCATIONS          = 52
PASS_REASSOCIATE                = 53
PASS_DEMOTE_REGISTER_TO_MEMORY  = 54
PASS_SCALAR_REPL_AGGREGATES     = 55
PASS_SCCP                       = 56
PASS_SIMPLIFY_LIB_CALLS         = 57
PASS_CFG_SIMPLIFICATION         = 58
PASS_STRIP_SYMBOLS              = 59
PASS_STRIP_DEAD_PROTOTYPES      = 60
PASS_STRUCT_RET_PROMOTION       = 61
PASS_TAIL_CALL_ELIMINATION      = 62
PASS_TAIL_DUPLICATION           = 63



#===----------------------------------------------------------------------===
# Helper functions
#===----------------------------------------------------------------------===

_pass_creator = {
    PASS_AGGRESSIVE_DCE             : _core.LLVMAddAggressiveDCEPass,
    PASS_ARGUMENT_PROMOTION         : _core.LLVMAddArgumentPromotionPass,
    PASS_BLOCK_PLACEMENT            : _core.LLVMAddBlockPlacementPass,
    PASS_BREAK_CRITICAL_EDGES       : _core.LLVMAddBreakCriticalEdgesPass,
    PASS_CODE_GEN_PREPARE           : _core.LLVMAddCodeGenPreparePass,
    PASS_COND_PROPAGATION           : _core.LLVMAddCondPropagationPass,
    PASS_CONSTANT_MERGE             : _core.LLVMAddConstantMergePass,
    PASS_CONSTANT_PROPAGATION       : _core.LLVMAddConstantPropagationPass,
    PASS_DEAD_CODE_ELIMINATION      : _core.LLVMAddDeadCodeEliminationPass,
    PASS_DEAD_ARG_ELIMINATION       : _core.LLVMAddDeadArgEliminationPass,
    PASS_DEAD_TYPE_ELIMINATION      : _core.LLVMAddDeadTypeEliminationPass,
    PASS_DEAD_INST_ELIMINATION      : _core.LLVMAddDeadInstEliminationPass,
    PASS_DEAD_STORE_ELIMINATION     : _core.LLVMAddDeadStoreEliminationPass,
    # PASS_GCSE                       : _core.LLVMAddGCSEPass,: removed in LLVM 2.4.
    PASS_GLOBAL_DCE                 : _core.LLVMAddGlobalDCEPass,
    PASS_GLOBAL_OPTIMIZER           : _core.LLVMAddGlobalOptimizerPass,
    PASS_GVN                        : _core.LLVMAddGVNPass,
    PASS_GVNPRE                     : _core.LLVMAddGVNPREPass,
    PASS_IND_MEM_REM                : _core.LLVMAddIndMemRemPass,
    PASS_IND_VAR_SIMPLIFY           : _core.LLVMAddIndVarSimplifyPass,
    PASS_FUNCTION_INLINING          : _core.LLVMAddFunctionInliningPass,
    PASS_BLOCK_PROFILER             : _core.LLVMAddBlockProfilerPass,
    PASS_EDGE_PROFILER              : _core.LLVMAddEdgeProfilerPass,
    PASS_FUNCTION_PROFILER          : _core.LLVMAddFunctionProfilerPass,
    PASS_NULL_PROFILER_RS           : _core.LLVMAddNullProfilerRSPass,
    PASS_RS_PROFILING               : _core.LLVMAddRSProfilingPass,
    PASS_INSTRUCTION_COMBINING      : _core.LLVMAddInstructionCombiningPass,
    PASS_INTERNALIZE                : _core.LLVMAddInternalizePass,
    PASS_IP_CONSTANT_PROPAGATION    : _core.LLVMAddIPConstantPropagationPass,
    PASS_IPSCCP                     : _core.LLVMAddIPSCCPPass,
    PASS_JUMP_THREADING             : _core.LLVMAddJumpThreadingPass,
    PASS_LCSSA                      : _core.LLVMAddLCSSAPass,
    PASS_LICM                       : _core.LLVMAddLICMPass,
    PASS_LOOP_DELETION              : _core.LLVMAddLoopDeletionPass,
    PASS_LOOP_EXTRACTOR             : _core.LLVMAddLoopExtractorPass,
    PASS_SINGLE_LOOP_EXTRACTOR      : _core.LLVMAddSingleLoopExtractorPass,
    PASS_LOOP_INDEX_SPLIT           : _core.LLVMAddLoopIndexSplitPass,
    PASS_LOOP_STRENGTH_REDUCE       : _core.LLVMAddLoopStrengthReducePass,
    PASS_LOOP_ROTATE                : _core.LLVMAddLoopRotatePass,
    PASS_LOOP_UNROLL                : _core.LLVMAddLoopUnrollPass,
    PASS_LOOP_UNSWITCH              : _core.LLVMAddLoopUnswitchPass,
    PASS_LOOP_SIMPLIFY              : _core.LLVMAddLoopSimplifyPass,
    PASS_LOWER_ALLOCATIONS          : _core.LLVMAddLowerAllocationsPass,
    PASS_LOWER_INVOKE               : _core.LLVMAddLowerInvokePass,
    PASS_LOWER_SET_JMP              : _core.LLVMAddLowerSetJmpPass,
    PASS_LOWER_SWITCH               : _core.LLVMAddLowerSwitchPass,
    PASS_PROMOTE_MEMORY_TO_REGISTER : _core.LLVMAddPromoteMemoryToRegisterPass,
    PASS_MEM_CPY_OPT                : _core.LLVMAddMemCpyOptPass,
    PASS_UNIFY_FUNCTION_EXIT_NODES  : _core.LLVMAddUnifyFunctionExitNodesPass,
    PASS_PREDICATE_SIMPLIFIER       : _core.LLVMAddPredicateSimplifierPass,
    PASS_PRUNE_EH                   : _core.LLVMAddPruneEHPass,
    PASS_RAISE_ALLOCATIONS          : _core.LLVMAddRaiseAllocationsPass,
    PASS_REASSOCIATE                : _core.LLVMAddReassociatePass,
    PASS_DEMOTE_REGISTER_TO_MEMORY  : _core.LLVMAddDemoteRegisterToMemoryPass,
    PASS_SCALAR_REPL_AGGREGATES     : _core.LLVMAddScalarReplAggregatesPass,
    PASS_SCCP                       : _core.LLVMAddSCCPPass,
    PASS_SIMPLIFY_LIB_CALLS         : _core.LLVMAddSimplifyLibCallsPass,
    PASS_CFG_SIMPLIFICATION         : _core.LLVMAddCFGSimplificationPass,
    PASS_STRIP_SYMBOLS              : _core.LLVMAddStripSymbolsPass,
    PASS_STRIP_DEAD_PROTOTYPES      : _core.LLVMAddStripDeadPrototypesPass,
    PASS_STRUCT_RET_PROMOTION       : _core.LLVMAddStructRetPromotionPass,
    PASS_TAIL_CALL_ELIMINATION      : _core.LLVMAddTailCallEliminationPass,
    PASS_TAIL_DUPLICATION           : _core.LLVMAddTailDuplicationPass,
}


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

    def add(self, tgt_data_or_pass_id):
        if isinstance(tgt_data_or_pass_id, ee.TargetData):
            self._add_target_data(tgt_data_or_pass_id)
        elif tgt_data_or_pass_id in _pass_creator:
            self._add_pass(tgt_data_or_pass_id)
        else:
            raise llvm.LLVMException, ("invalid pass_id (%s)" % str(tgt_data_or_pass_id))

    def _add_target_data(self, tgt):
        _core.LLVMAddTargetData(tgt.ptr, self.ptr)

    def _add_pass(self, pass_id):
        cfn = _pass_creator[pass_id]
        cfn(self.ptr)

    def run(self, module):
        core.check_is_module(module)
        return _core.LLVMRunPassManager(self.ptr, module.ptr)


class FunctionPassManager(PassManager):

    @staticmethod
    def new(mp):
        core.check_is_module_provider(mp)
        return FunctionPassManager(_core.LLVMCreateFunctionPassManager(mp.ptr))

    def __init__(self, ptr):
        PassManager.__init__(self, ptr)

    def initialize(self):
        _core.LLVMInitializeFunctionPassManager(self.ptr)

    def run(self, fn):
        core.check_is_function(fn)
        return _core.LLVMRunFunctionPassManager(self.ptr, fn.ptr)

    def finalize(self):
        _core.LLVMFinalizeFunctionPassManager(self.ptr)

