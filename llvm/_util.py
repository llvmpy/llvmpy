"""Utility functions and classes.

Not for public use!"""

import core

def _check_gen(obj, type):
    if not isinstance(obj, type):
        msg = "argument must be an instance of llvm.core.%s (or of a class derived from it)" % type_str
        raise TypeError, msg

def check_is_type(obj):     _check_gen(obj, core.Type)
def check_is_value(obj):    _check_gen(obj, core.Value)
def check_is_pointer(obj):  _check_gen(obj, core.Pointer)
def check_is_constant(obj): _check_gen(obj, core.Constant)
def check_is_function(obj): _check_gen(obj, core.Function)
def check_is_basic_block(obj): _check_gen(obj, core.BasicBlock)
def check_is_module_provider(obj): _check_gen(obj, core.ModuleProvider)

def unpack_gen(objlist, check_fn):
    for obj in objlist: check_fn(obj)
    return [ obj.ptr for obj in objlist ]

def unpack_types(objlist):     return unpack_gen(objlist, check_is_type)
def unpack_values(objlist):    return unpack_gen(objlist, check_is_value)
def unpack_constants(objlist): return unpack_gen(objlist, check_is_constant)

def wrapiter(first, next, container, wrapper):
    ptr = first(container)
    while ptr:
        yield wrapper(ptr)
        ptr = next(ptr)

class dummy_owner(object):

    def __init__(self, ownee):
        ownee._own(self)


