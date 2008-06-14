"""Execution Engine and related classes.

"""

import llvm             # top-level, for common stuff
import core             # module provider, function etc.
import _core            # C wrappers
from _util import *     # utility functions


#===----------------------------------------------------------------------===
# Target data
#===----------------------------------------------------------------------===

class TargetData(llvm.Ownable):

    @staticmethod
    def new(strrep):
        return TargetData(_core.LLVMCreateTargetData(strrep))

    def __init__(self, ptr):
        llvm.Ownable.__init__(self, ptr, _core.LLVMDisposeTargetData)

    def __str__(self):
        return _core.LLVMTargetDataAsString(self.ptr)


#===----------------------------------------------------------------------===
# Execution engine
#===----------------------------------------------------------------------===

class ExecutionEngine(object):

    @staticmethod
    def new(mp, force_interpreter=False):
        check_is_module_provider(mp)
        check_is_unowned(mp)
        ret = _core.LLVMCreateExecutionEngine(mp.ptr, int(force_interpreter))
        if isinstance(ret, str):
            raise llvm.LLVMException, ret
        return ExecutionEngine(ret, mp)

    def __init__(self, ptr, mp):
        self.ptr = ptr
        mp._own(self)

    def __del__(self):
        _core.LLVMDisposeExecutionEngine(self.ptr)

    def run_function(self, fn, args):
        check_is_function(fn)
        return _core.LLVMRunFunction(self.ptr, fn.ptr, args)

    @property
    def target_data(self):
        td = TargetData(_core.LLVMGetExecutionEngineTargetData(self.ptr))
        td._own(self)
        return td

