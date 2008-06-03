
from _util import *
import _core

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

    def add(self, pass_id):
        assert pass_id in _pass_creator, 'Invalid pass_id ("' + str(pass_id) + '")'
        cfn = _pass_creator[pass_id] # KeyError => pass_id is invalid
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

    def __del__(self):
        PassManager.__del__(self)

    def initialize(self):
        _core.LLVMInitializeFunctionPassManager(self.ptr)

    def run(self, fn):
        _check_is_function(fn)
        return _core.LLVMRunFunctionPassManager(fn.ptr)

    def finalize(self):
        _core.LLVMFinalizeFunctionPassManager(self.ptr)

