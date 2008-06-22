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
# Generic value
#===----------------------------------------------------------------------===

class GenericValue(object):

    @staticmethod
    def int(ty, intval):
        check_is_type(ty)
        ptr = _core.LLVMCreateGenericValueOfInt(ty.ptr, intval, 0)
        return GenericValue(ptr)

    @staticmethod
    def int_signed(ty, intval):
        check_is_type(ty)
        ptr = _core.LLVMCreateGenericValueOfInt(ty.ptr, intval, 1)
        return GenericValue(ptr)

    @staticmethod
    def real(ty, floatval):
        check_is_type(ty)   # only float or double
        ptr = _core.LLVMCreateGenericValueOfFloat(ty.ptr, floatval)
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
        check_is_type(ty)   # only float or double
        return _core.LLVMGenericValueToFloat(ty.ptr, self.ptr)


# helper functions for generic value objects
def _check_is_generic_value(obj): check_gen(obj, GenericValue)
def _unpack_generic_values(objlist): 
    return unpack_gen(objlist, _check_is_generic_value)


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
        ptrs = _unpack_generic_values(args)
        gvptr = _core.LLVMRunFunction2(self.ptr, fn.ptr, ptrs)
        return GenericValue(gvptr)

    def run_static_ctors(self):
        _core.LLVMRunStaticConstructors(self.ptr)

    def run_static_dtors(self):
        _core.LLVMRunStaticDestructors(self.ptr)

    def free_machine_code_for(self, fn):
        check_is_function(fn)
        _core.LLVMFreeMachineCodeForFunction(self.ptr, fn.ptr)

    def add_module_provider(self, mp):
        check_is_module_provider(mp)
        _core.LLVMAddModuleProvider(self.ptr, mp.ptr)

    @property
    def target_data(self):
        td = TargetData(_core.LLVMGetExecutionEngineTargetData(self.ptr))
        td._own(self)
        return td

