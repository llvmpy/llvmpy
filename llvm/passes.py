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


# passes
PASS_AAEVAL                          = 1
PASS_ABCD                            = 2
PASS_AGGRESSIVE_DCE                  = 3
PASS_ALIAS_ANALYSIS_COUNTER          = 4
PASS_ALWAYS_INLINER                  = 5
PASS_ARGUMENT_PROMOTION              = 6
PASS_BASIC_ALIAS_ANALYSIS            = 7
PASS_BLOCK_PLACEMENT                 = 8
PASS_BREAK_CRITICAL_EDGES            = 9
PASS_CFG_SIMPLIFICATION              = 10
PASS_CODE_GEN_PREPARE                = 11
PASS_CONSTANT_MERGE                  = 12
PASS_CONSTANT_PROPAGATION            = 13
PASS_DBG_INFO_PRINTER                = 14
PASS_DEAD_ARG_ELIMINATION            = 15
PASS_DEAD_CODE_ELIMINATION           = 16
PASS_DEAD_INST_ELIMINATION           = 17
PASS_DEAD_STORE_ELIMINATION          = 18
PASS_DEAD_TYPE_ELIMINATION           = 19
PASS_DEMOTE_REGISTER_TO_MEMORY       = 20
PASS_DOM_ONLY_PRINTER                = 21
PASS_DOM_ONLY_VIEWER                 = 22
PASS_DOM_PRINTER                     = 23
PASS_DOM_VIEWER                      = 24
PASS_EDGE_PROFILER                   = 25
PASS_FUNCTION_ATTRS                  = 26
PASS_FUNCTION_INLINING               = 27
PASS_GEP_SPLITTER                    = 28
PASS_GLOBAL_DCE                      = 29
PASS_GLOBAL_OPTIMIZER                = 30
PASS_GLOBALS_MOD_REF                 = 31
PASS_GVN                             = 32
PASS_IND_VAR_SIMPLIFY                = 33
PASS_INST_COUNT                      = 34
PASS_INSTRUCTION_COMBINING           = 35
PASS_INSTRUCTION_NAMER               = 36
PASS_IP_CONSTANT_PROPAGATION         = 37
PASS_IPSCCP                          = 38
PASS_JUMP_THREADING                  = 39
PASS_LAZY_VALUE_INFO                 = 40
PASS_LCSSA                           = 41
PASS_LICM                            = 42
PASS_LIVE_VALUES                     = 43
PASS_LOOP_DELETION                   = 44
PASS_LOOP_DEPENDENCE_ANALYSIS        = 45
PASS_LOOP_EXTRACTOR                  = 46
PASS_LOOP_INDEX_SPLIT                = 47
PASS_LOOP_ROTATE                     = 48
PASS_LOOP_SIMPLIFY                   = 49
PASS_LOOP_STRENGTH_REDUCE            = 50
PASS_LOOP_UNROLL                     = 51
PASS_LOOP_UNSWITCH                   = 52
PASS_LOWER_INVOKE                    = 53
PASS_LOWER_SET_JMP                   = 54
PASS_LOWER_SWITCH                    = 55
PASS_MEM_CPY_OPT                     = 56
PASS_MERGE_FUNCTIONS                 = 57
PASS_NO_AA                           = 58
PASS_NO_PROFILE_INFO                 = 59
PASS_OPTIMAL_EDGE_PROFILER           = 60
PASS_PARTIAL_INLINING                = 61
PASS_PARTIAL_SPECIALIZATION          = 62
PASS_POST_DOM_ONLY_PRINTER           = 63
PASS_POST_DOM_ONLY_VIEWER            = 64
PASS_POST_DOM_PRINTER                = 65
PASS_POST_DOM_VIEWER                 = 66
PASS_PROFILE_ESTIMATOR               = 67
PASS_PROFILE_LOADER                  = 68
PASS_PROFILE_VERIFIER                = 69
PASS_PROMOTE_MEMORY_TO_REGISTER      = 70
PASS_PRUNE_EH                        = 71
PASS_REASSOCIATE                     = 72
PASS_SCALAR_EVOLUTION_ALIAS_ANALYSIS = 73
PASS_SCALAR_REPL_AGGREGATES          = 74
PASS_SCCVN                           = 75
PASS_SCCP                            = 76
PASS_SIMPLIFY_HALF_POWR_LIB_CALLS    = 77
PASS_SIMPLIFY_LIB_CALLS              = 78
PASS_SINGLE_LOOP_EXTRACTOR           = 79
PASS_SSI                             = 80
PASS_SSI_EVERYTHING                  = 81
PASS_STRIP_DEAD_PROTOTYPES           = 82
PASS_STRIP_NON_DEBUG_SYMBOLS         = 83
PASS_STRIP_SYMBOLS                   = 84
PASS_STRUCT_RET_PROMOTION            = 85
PASS_TAIL_CALL_ELIMINATION           = 86
PASS_TAIL_DUPLICATION                = 87
PASS_UNIFY_FUNCTION_EXIT_NODES       = 88
PASS_INTERNALIZE                     = 89



#===----------------------------------------------------------------------===
# Helper functions
#===----------------------------------------------------------------------===

_pass_creator = {
    PASS_AAEVAL                          : _core.LLVMAddAAEvalPass,
    PASS_ABCD                            : _core.LLVMAddABCDPass,
    PASS_AGGRESSIVE_DCE                  : _core.LLVMAddAggressiveDCEPass,
    PASS_ALIAS_ANALYSIS_COUNTER          : _core.LLVMAddAliasAnalysisCounterPass,
    PASS_ALWAYS_INLINER                  : _core.LLVMAddAlwaysInlinerPass,
    PASS_ARGUMENT_PROMOTION              : _core.LLVMAddArgumentPromotionPass,
    PASS_BASIC_ALIAS_ANALYSIS            : _core.LLVMAddBasicAliasAnalysisPass,
    PASS_BLOCK_PLACEMENT                 : _core.LLVMAddBlockPlacementPass,
    PASS_BREAK_CRITICAL_EDGES            : _core.LLVMAddBreakCriticalEdgesPass,
    PASS_CFG_SIMPLIFICATION              : _core.LLVMAddCFGSimplificationPass,
    PASS_CODE_GEN_PREPARE                : _core.LLVMAddCodeGenPreparePass,
    PASS_CONSTANT_MERGE                  : _core.LLVMAddConstantMergePass,
    PASS_CONSTANT_PROPAGATION            : _core.LLVMAddConstantPropagationPass,
    PASS_DBG_INFO_PRINTER                : _core.LLVMAddDbgInfoPrinterPass,
    PASS_DEAD_ARG_ELIMINATION            : _core.LLVMAddDeadArgEliminationPass,
    PASS_DEAD_CODE_ELIMINATION           : _core.LLVMAddDeadCodeEliminationPass,
    PASS_DEAD_INST_ELIMINATION           : _core.LLVMAddDeadInstEliminationPass,
    PASS_DEAD_STORE_ELIMINATION          : _core.LLVMAddDeadStoreEliminationPass,
    PASS_DEAD_TYPE_ELIMINATION           : _core.LLVMAddDeadTypeEliminationPass,
    PASS_DEMOTE_REGISTER_TO_MEMORY       : _core.LLVMAddDemoteRegisterToMemoryPass,
    PASS_DOM_ONLY_PRINTER                : _core.LLVMAddDomOnlyPrinterPass,
    PASS_DOM_ONLY_VIEWER                 : _core.LLVMAddDomOnlyViewerPass,
    PASS_DOM_PRINTER                     : _core.LLVMAddDomPrinterPass,
    PASS_DOM_VIEWER                      : _core.LLVMAddDomViewerPass,
    PASS_EDGE_PROFILER                   : _core.LLVMAddEdgeProfilerPass,
    PASS_FUNCTION_ATTRS                  : _core.LLVMAddFunctionAttrsPass,
    PASS_FUNCTION_INLINING               : _core.LLVMAddFunctionInliningPass,
    PASS_GEP_SPLITTER                    : _core.LLVMAddGEPSplitterPass,
    PASS_GLOBAL_DCE                      : _core.LLVMAddGlobalDCEPass,
    PASS_GLOBAL_OPTIMIZER                : _core.LLVMAddGlobalOptimizerPass,
    PASS_GLOBALS_MOD_REF                 : _core.LLVMAddGlobalsModRefPass,
    PASS_GVN                             : _core.LLVMAddGVNPass,
    PASS_IND_VAR_SIMPLIFY                : _core.LLVMAddIndVarSimplifyPass,
    PASS_INST_COUNT                      : _core.LLVMAddInstCountPass,
    PASS_INSTRUCTION_COMBINING           : _core.LLVMAddInstructionCombiningPass,
    PASS_INSTRUCTION_NAMER               : _core.LLVMAddInstructionNamerPass,
    PASS_IP_CONSTANT_PROPAGATION         : _core.LLVMAddIPConstantPropagationPass,
    PASS_IPSCCP                          : _core.LLVMAddIPSCCPPass,
    PASS_JUMP_THREADING                  : _core.LLVMAddJumpThreadingPass,
    PASS_LAZY_VALUE_INFO                 : _core.LLVMAddLazyValueInfoPass,
    PASS_LCSSA                           : _core.LLVMAddLCSSAPass,
    PASS_LICM                            : _core.LLVMAddLICMPass,
    PASS_LIVE_VALUES                     : _core.LLVMAddLiveValuesPass,
    PASS_LOOP_DELETION                   : _core.LLVMAddLoopDeletionPass,
    PASS_LOOP_DEPENDENCE_ANALYSIS        : _core.LLVMAddLoopDependenceAnalysisPass,
    PASS_LOOP_EXTRACTOR                  : _core.LLVMAddLoopExtractorPass,
    PASS_LOOP_INDEX_SPLIT                : _core.LLVMAddLoopIndexSplitPass,
    PASS_LOOP_ROTATE                     : _core.LLVMAddLoopRotatePass,
    PASS_LOOP_SIMPLIFY                   : _core.LLVMAddLoopSimplifyPass,
    PASS_LOOP_STRENGTH_REDUCE            : _core.LLVMAddLoopStrengthReducePass,
    PASS_LOOP_UNROLL                     : _core.LLVMAddLoopUnrollPass,
    PASS_LOOP_UNSWITCH                   : _core.LLVMAddLoopUnswitchPass,
    PASS_LOWER_INVOKE                    : _core.LLVMAddLowerInvokePass,
    PASS_LOWER_SET_JMP                   : _core.LLVMAddLowerSetJmpPass,
    PASS_LOWER_SWITCH                    : _core.LLVMAddLowerSwitchPass,
    PASS_MEM_CPY_OPT                     : _core.LLVMAddMemCpyOptPass,
    PASS_MERGE_FUNCTIONS                 : _core.LLVMAddMergeFunctionsPass,
    PASS_NO_AA                           : _core.LLVMAddNoAAPass,
    PASS_NO_PROFILE_INFO                 : _core.LLVMAddNoProfileInfoPass,
    PASS_OPTIMAL_EDGE_PROFILER           : _core.LLVMAddOptimalEdgeProfilerPass,
    PASS_PARTIAL_INLINING                : _core.LLVMAddPartialInliningPass,
    PASS_PARTIAL_SPECIALIZATION          : _core.LLVMAddPartialSpecializationPass,
    PASS_POST_DOM_ONLY_PRINTER           : _core.LLVMAddPostDomOnlyPrinterPass,
    PASS_POST_DOM_ONLY_VIEWER            : _core.LLVMAddPostDomOnlyViewerPass,
    PASS_POST_DOM_PRINTER                : _core.LLVMAddPostDomPrinterPass,
    PASS_POST_DOM_VIEWER                 : _core.LLVMAddPostDomViewerPass,
    PASS_PROFILE_ESTIMATOR               : _core.LLVMAddProfileEstimatorPass,
    PASS_PROFILE_LOADER                  : _core.LLVMAddProfileLoaderPass,
    PASS_PROFILE_VERIFIER                : _core.LLVMAddProfileVerifierPass,
    PASS_PROMOTE_MEMORY_TO_REGISTER      : _core.LLVMAddPromoteMemoryToRegisterPass,
    PASS_PRUNE_EH                        : _core.LLVMAddPruneEHPass,
    PASS_REASSOCIATE                     : _core.LLVMAddReassociatePass,
    PASS_SCALAR_EVOLUTION_ALIAS_ANALYSIS : _core.LLVMAddScalarEvolutionAliasAnalysisPass,
    PASS_SCALAR_REPL_AGGREGATES          : _core.LLVMAddScalarReplAggregatesPass,
    PASS_SCCVN                           : _core.LLVMAddSCCVNPass,
    PASS_SCCP                            : _core.LLVMAddSCCPPass,
    PASS_SIMPLIFY_HALF_POWR_LIB_CALLS    : _core.LLVMAddSimplifyHalfPowrLibCallsPass,
    PASS_SIMPLIFY_LIB_CALLS              : _core.LLVMAddSimplifyLibCallsPass,
    PASS_SINGLE_LOOP_EXTRACTOR           : _core.LLVMAddSingleLoopExtractorPass,
    PASS_SSI                             : _core.LLVMAddSSIPass,
    PASS_SSI_EVERYTHING                  : _core.LLVMAddSSIEverythingPass,
    PASS_STRIP_DEAD_PROTOTYPES           : _core.LLVMAddStripDeadPrototypesPass,
    PASS_STRIP_NON_DEBUG_SYMBOLS         : _core.LLVMAddStripNonDebugSymbolsPass,
    PASS_STRIP_SYMBOLS                   : _core.LLVMAddStripSymbolsPass,
    PASS_STRUCT_RET_PROMOTION            : _core.LLVMAddStructRetPromotionPass,
    PASS_TAIL_CALL_ELIMINATION           : _core.LLVMAddTailCallEliminationPass,
    PASS_TAIL_DUPLICATION                : _core.LLVMAddTailDuplicationPass,
    PASS_UNIFY_FUNCTION_EXIT_NODES       : _core.LLVMAddUnifyFunctionExitNodesPass,
    PASS_INTERNALIZE                     : _core.LLVMAddInternalizePass,
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
            raise llvm.LLVMException, \
                ("invalid pass_id (%s)" % str(tgt_data_or_pass_id))

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

