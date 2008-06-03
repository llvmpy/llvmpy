"""Execution Engine and related classes.

"""

import llvm, core
from _util import *
import _core

class ExecutionEngine(object):

    @staticmethod
    def new(mp, force_interpreter=False):
        check_is_module_provider(mp)
        ret = _core.LLVMCreateExecutionEngine(mp.ptr, int(create_interpreter))
        if isinstance(ret, str):
            raise llvm.LLVMException, str
        return ExecutionEngine(ret)

    def __init__(self, ptr):
        self.ptr = ptr

    def __del__(self):
        _core.LLVMDisposeExecutionEngine(self.ptr)

    def run_static_constructors(self):
        _core.LLVMRunStaticConstructors(self.ptr)

    def run_static_destructors(self):
        _core.LLVMRunStaticDestructors(self.ptr)

    def run_function_as_main(self, fn, argv, envp):
        check_is_function(fn)
        _core.LLVMRunFunctionAsMain(self.ptr, fn.ptr, argv, envp)

    def run_function(self, fn, args):
        check_is_function(fn)
        return _core.LLVMRunFunction(self.ptr, fn.ptr, args)

    def free_machine_code_for_function(self, fn):
        check_is_function(fn)
        _core.LLVMFreeMachineCodeForFunction(self.ptr, fn.ptr)

    def add_module_provider(self, mp):
        pass

    def remove_module_provider(self):
        pass

    @property
    def target_data(self):
        return TargetData(_core.LLVMGetExecutionEngineTargetData(self.ptr))
