#
# Copyright (c) 2008, Mahadevan R All rights reserved.
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

"""Common classes related to LLVM.

"""

VERSION = '0.6'

from weakref import WeakValueDictionary


#===----------------------------------------------------------------------===
# Exceptions
#===----------------------------------------------------------------------===

class LLVMException(Exception):
    """Generic LLVM exception."""

    def __init__(self, msg=""):
        Exception.__init__(self, msg)


#===----------------------------------------------------------------------===
# Ownables
#===----------------------------------------------------------------------===

class Ownable(object):
    """Objects that can be owned.

    Modules and Module Providers can be owned, i.e., the responsibility of
    destruction of ownable objects can be handed over to other objects. The
    llvm.Ownable class represents objects that can be so owned. This class
    is NOT intended for public use.
    """

    def __init__(self, ptr, del_fn):
        self.ptr = ptr
        self.owner = None
        self.del_fn = del_fn

    def _own(self, owner):
        if self.owner:
            raise LLVMException, "object already owned"
        self.owner = owner

    def _disown(self):
        if not self.owner:
            raise LLVMException, "not owned"
        self.owner = None

    def __del__(self):
        if not self.owner:
            self.del_fn(self.ptr)


#===----------------------------------------------------------------------===
# Dummy owner, will not delete ownee. Be careful.
#===----------------------------------------------------------------------===

class DummyOwner(object):
    pass


#===----------------------------------------------------------------------===
# A metaclass to prevent aliasing.  It stores a (weak) reference to objects
# constructed based on a PyCObject.  If an object is constructed based on a
# PyCObject with the same underlying pointer as a previous object, a reference
# to the previous object is returned rather than a new one.
#===----------------------------------------------------------------------===

class _ObjectCache(type):
    """A metaclass to prevent aliasing.

    Classes using 'ObjectCache' as a metaclass must have constructors
    that take a PyCObject as their first argument.  When the class is
    called (to create a new instance of the class), the value of the
    pointer wrapped by the PyCObj is checked:

        If no previous object has been created based on the same
        underlying pointer (note that different PyCObject objects can
        wrap the same pointer), the object will be initialized as
        usual and returned.

        If a previous has been created based on the same pointer,
        then a reference to that object will be returned, and no
        object initialization is performed.
    """

    __instances = WeakValueDictionary()

    def __call__(cls, ptr, *args, **kwargs):
        objid = _core.PyCObjectVoidPtrToPyLong(ptr)
        obj = _ObjectCache.__instances.get(objid)
        if obj is None:
            obj = super(_ObjectCache, cls).__call__(ptr, *args, **kwargs)
            _ObjectCache.__instances[objid] = obj
        return obj

    @staticmethod
    def forget(obj):
        objid = _core.PyCObjectVoidPtrToPyLong(obj.ptr)
        if objid in _ObjectCache.__instances:
            del _ObjectCache.__instances[objid]


#===----------------------------------------------------------------------===
# Cacheables
#===----------------------------------------------------------------------===

class Cacheable(object):
    """Objects that can be cached.

    Objects that wrap a PyCObject are cached to avoid "aliasing", i.e.,
    two Python objects each containing a PyCObject which internally points
    to the same C pointer."""

    __metaclass__ = _ObjectCache

    def forget(self):
        _ObjectCache.forget(self)

