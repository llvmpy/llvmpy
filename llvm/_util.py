"""Utility functions and classes.

Used only in other modules, not for public use."""

import core
import llvm


#===----------------------------------------------------------------------===
# A set of helpers to check various things. Raises exceptions on
# failures.
#===----------------------------------------------------------------------===

def _check_gen(obj, type):
    if not isinstance(obj, type):
        type_str = type.__name__
        msg = "argument not an instance of llvm.core.%s" % type_str
        raise TypeError, msg

def check_is_type(obj):     _check_gen(obj, core.Type)
def check_is_value(obj):    _check_gen(obj, core.Value)
def check_is_pointer(obj):  _check_gen(obj, core.Pointer)
def check_is_constant(obj): _check_gen(obj, core.Constant)
def check_is_function(obj): _check_gen(obj, core.Function)
def check_is_basic_block(obj): _check_gen(obj, core.BasicBlock)
def check_is_module(obj):   _check_gen(obj, core.Module)
def check_is_module_provider(obj): _check_gen(obj, core.ModuleProvider)

def check_is_unowned(ownable):
    if ownable.owner:
        raise llvm.LLVMException, "object is already owned"


#===----------------------------------------------------------------------===
# A set of helpers to unpack a list of Python wrapper objects
# into a list of PyCObject wrapped objects, checking types along
# the way.
#===----------------------------------------------------------------------===

def _unpack_gen(objlist, check_fn):
    for obj in objlist: check_fn(obj)
    return [ obj.ptr for obj in objlist ]

def unpack_types(objlist):     return _unpack_gen(objlist, check_is_type)
def unpack_values(objlist):    return _unpack_gen(objlist, check_is_value)
def unpack_constants(objlist): return _unpack_gen(objlist, check_is_constant)


#===----------------------------------------------------------------------===
# Helper to wrap over iterables (LLVMFirstXXX, LLVMNextXXX). This used
# to be a generator, but that loses subscriptability of the result, so
# we now return a list.
#===----------------------------------------------------------------------===

def wrapiter(first, next, container, wrapper, extra=[]):
#    ptr = first(container)
#    while ptr:
#        yield wrapper(ptr)
#        ptr = next(ptr)
    ret = []
    ptr = first(container)
    while ptr:
        ret.append(wrapper(ptr, *extra))
        ptr = next(ptr)
    return ret


#===----------------------------------------------------------------------===
# Dummy owner, will not delete ownee. Be careful.
#===----------------------------------------------------------------------===

class dummy_owner(object):

    def __init__(self, ownee):
        ownee._own(self)

