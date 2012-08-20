"""
Common classes related to LLVM.
"""

__version__ = '0.8.2'


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
            raise LLVMException("object already owned")
        self.owner = owner

    def _disown(self):
        if not self.owner:
            raise LLVMException("not owned")
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
        key = "%s:%d" % (cls.__name__, objid)
        obj = _ObjectCache.__instances.get(key)
        if obj is None:
            obj = super(_ObjectCache, cls).__call__(ptr, *args, **kwargs)
            _ObjectCache.__instances[key] = obj
        return obj

    @staticmethod
    def forget(obj):
        objid = _core.PyCObjectVoidPtrToPyLong(obj.ptr)
        key = "%s:%d" % (type(obj).__name__, objid)
        if key in _ObjectCache.__instances:
            del _ObjectCache.__instances[key]


#===----------------------------------------------------------------------===
# Cacheables
#===----------------------------------------------------------------------===

# version 2/3 compatibility help
#   version 2 metaclass
#       class Cacheable(object):
#           __metaclass__ = _ObjectCache  # Doing nothing for version 3
#
#   version 3 metaclass
#       class Cacheable(metaclass=_ObjectCache):
#
# Reference: http://mikewatkins.ca/2008/11/29/python-2-and-3-metaclasses/#using-the-metaclass-in-python-3-x
ObjectCache = _ObjectCache('ObjectCache', (object, ), {})

class Cacheable(ObjectCache):
    """Objects that can be cached.

    Objects that wrap a PyCObject are cached to avoid "aliasing", i.e.,
    two Python objects each containing a PyCObject which internally points
    to the same C pointer."""

    def forget(self):
        ObjectCache.forget(self)


def test(verbosity=1):
    """test(verbosity=1) -> TextTestResult

    Run self-test, and return unittest.runner.TextTestResult object.
    """
    from llvm.test_llvmpy import run

    return run(verbosity=verbosity)
