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

"""Execution Engine and related classes.

"""

import llvm                 # top-level, for common stuff
import llvm.core as core    # module, function etc.
import llvm._core as _core  # C wrappers
import llvm._util as _util  # utility functions


#===----------------------------------------------------------------------===
# Enumerations
#===----------------------------------------------------------------------===

BO_BIG_ENDIAN       = 0
BO_LITTLE_ENDIAN    = 1


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
            raise core.LLVMException, \
                "argument is neither a type nor a global variable"

    def element_at_offset(self, ty, ofs):
        core.check_is_type_struct(ty)
        ofs = long(ofs) # ofs is unsigned long long
        return _core.LLVMElementAtOffset(self.ptr, ty.ptr, ofs)

    def offset_of_element(self, ty, el):
        core.check_is_type_struct(ty)
        el = int(el) # el should be an int
        return _core.LLVMOffsetOfElement(self.ptr, ty.ptr, el)


#===----------------------------------------------------------------------===
# Generic value
#===----------------------------------------------------------------------===

class GenericValue(object):

    @staticmethod
    def int(ty, intval):
        core.check_is_type(ty)
        ptr = _core.LLVMCreateGenericValueOfInt(ty.ptr, intval, 0)
        return GenericValue(ptr)

    @staticmethod
    def int_signed(ty, intval):
        core.check_is_type(ty)
        ptr = _core.LLVMCreateGenericValueOfInt(ty.ptr, intval, 1)
        return GenericValue(ptr)

    @staticmethod
    def real(ty, floatval):
        core.check_is_type(ty)   # only float or double
        ptr = _core.LLVMCreateGenericValueOfFloat(ty.ptr, floatval)
        return GenericValue(ptr)

    @staticmethod
    def pointer(ty, intval):
        core.check_is_type(ty)
        ptr = _core.LLVMCreateGenericValueOfPointer(ty.ptr, intval)
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
        core.check_is_type(ty)   # only float or double
        return _core.LLVMGenericValueToFloat(ty.ptr, self.ptr)

    def as_pointer(self):
        return _core.LLVMGenericValueToPointer(self.ptr)


# helper functions for generic value objects
def check_is_generic_value(obj): _util.check_gen(obj, GenericValue)
def _unpack_generic_values(objlist):
    return _util.unpack_gen(objlist, check_is_generic_value)


#===----------------------------------------------------------------------===
# Execution engine
#===----------------------------------------------------------------------===

class ExecutionEngine(object):

    @staticmethod
    def new(module, force_interpreter=False):
        core.check_is_module(module)
        _util.check_is_unowned(module)
        ret = _core.LLVMCreateExecutionEngine(module.ptr, int(force_interpreter))
        if isinstance(ret, str):
            raise llvm.LLVMException, ret
        return ExecutionEngine(ret, module)

    def __init__(self, ptr, module):
        self.ptr = ptr
        module._own(self)

    def __del__(self):
        _core.LLVMDisposeExecutionEngine(self.ptr)

    def run_function(self, fn, args):
        core.check_is_function(fn)
        ptrs = _unpack_generic_values(args)
        gvptr = _core.LLVMRunFunction2(self.ptr, fn.ptr, ptrs)
        return GenericValue(gvptr)

    def get_pointer_to_function(self, fn):
        core.check_is_function(fn)
        return _core.LLVMGetPointerToFunction(self.ptr,fn.ptr)

    def run_static_ctors(self):
        _core.LLVMRunStaticConstructors(self.ptr)

    def run_static_dtors(self):
        _core.LLVMRunStaticDestructors(self.ptr)

    def free_machine_code_for(self, fn):
        core.check_is_function(fn)
        _core.LLVMFreeMachineCodeForFunction(self.ptr, fn.ptr)

    def add_module(self, module):
        core.check_is_module(module)
        _core.LLVMAddModule(self.ptr, module.ptr)
        module._own(self)

    def remove_module(self, module):
        core.check_is_module(module)
        if module.owner != self:
            raise llvm.LLVMException, "module is not owned by self"
        ret = _core.LLVMRemoveModule2(self.ptr, module.ptr)
        if isinstance(ret, str):
            raise llvm.LLVMException, ret
        return core.Module(ret)

    @property
    def target_data(self):
        td = TargetData(_core.LLVMGetExecutionEngineTargetData(self.ptr))
        td._own(self)
        return td

