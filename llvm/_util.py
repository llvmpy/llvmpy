"""Utility functions and classes.

Used only in other modules, not for public use."""

import llvm


#===----------------------------------------------------------------------===
# A set of helpers to check various things. Raises exceptions on
# failures.
#===----------------------------------------------------------------------===

def check_gen(obj, type):
    if not isinstance(obj, type):
        type_str = type.__name__
        msg = "argument not an instance of llvm.core.%s" % type_str
        raise TypeError, msg

def check_is_unowned(ownable):
    if ownable.owner:
        raise llvm.LLVMException, "object is already owned"


#===----------------------------------------------------------------------===
# A set of helpers to unpack a list of Python wrapper objects
# into a list of PyCObject wrapped objects, checking types along
# the way.
#===----------------------------------------------------------------------===

def unpack_gen(objlist, check_fn):
    for obj in objlist: check_fn(obj)
    return [ obj.ptr for obj in objlist ]


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

