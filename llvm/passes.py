"""Pass managers and passes.

This module provides the LLVM pass managers and the passes themselves.
Passes that are currently available are:

  Simple Constant Propagation
  Combine Redundant Instructions
  Promote Memory to Register
  Demote all values to stack slots
  Reassociate expressions
  Global Value Numbering
  Simplify the CFG

See http://www.llvm.org/docs/Passes.html for the full list of passes
available in LLVM.
"""

import llvm.ee as ee        # target data
import llvm._core as _core  # C wrappers
from llvm._util import *    # utility functions


# passes
PASS_CONSTANT_PROPAGATION           = 1
PASS_INSTRUCTION_COMBINING          = 2
PASS_PROMOTE_MEMORY_TO_REGISTER     = 3
PASS_DEMOTE_MEMORY_TO_REGISTER      = 4
PASS_REASSOCIATE                    = 5
PASS_GVN                            = 6
PASS_CFG_SIMPLIFICATION             = 7


#===----------------------------------------------------------------------===
# Helper functions
#===----------------------------------------------------------------------===

_pass_creator = {
    PASS_CONSTANT_PROPAGATION       : _core.LLVMAddConstantPropagationPass,
    PASS_INSTRUCTION_COMBINING      : _core.LLVMAddInstructionCombiningPass,
    PASS_PROMOTE_MEMORY_TO_REGISTER : _core.LLVMAddPromoteMemoryToRegisterPass,
    PASS_DEMOTE_MEMORY_TO_REGISTER  : _core.LLVMAddDemoteMemoryToRegisterPass,
    PASS_REASSOCIATE                : _core.LLVMAddReassociatePass,
    PASS_GVN                        : _core.LLVMAddGVNPass,
    PASS_CFG_SIMPLIFICATION         : _core.LLVMAddCFGSimplificationPass,
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
            raise LLVMException, "invalid pass_id"

    def _add_target_data(self, tgt):
        _core.LLVMAddTargetData(tgt.ptr, self.ptr)

    def _add_pass(self, pass_id):
        cfn = _pass_creator[pass_id]
        cfn(self.ptr)

    def run(self, module):
        check_is_module(module)
        return _core.LLVMRunPassManager(self.ptr, module.ptr)


class FunctionPassManager(PassManager):

    @staticmethod
    def new(mp):
        check_is_module_provider(mp)
        return FunctionPassManager(_core.LLVMCreateFunctionPassManager(mp.ptr))

    def __init__(self, ptr):
        PassManager.__init__(self, ptr)

    def initialize(self):
        _core.LLVMInitializeFunctionPassManager(self.ptr)

    def run(self, fn):
        check_is_function(fn)
        return _core.LLVMRunFunctionPassManager(self.ptr, fn.ptr)

    def finalize(self):
        _core.LLVMFinalizeFunctionPassManager(self.ptr)

