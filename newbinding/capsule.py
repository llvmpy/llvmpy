import _capsule
from weakref import WeakValueDictionary

_pyclasses = {}
_addr2obj = WeakValueDictionary()


def _sentry(ptr):
    assert _capsule.check(ptr)


def classof(cap):
    cls = _capsule.getClassName(cap)
    return _pyclasses[cls]


def wrap(cap):
    '''Wrap a PyCapsule with the corresponding Wrapper class.
    If `cap` is not a PyCapsule, returns `cap`
    '''
    if not _capsule.check(cap):     # bypass if cap is not a PyCapsule
        return cap
    addr = _capsule.getPointer(cap)
    try:
        # find cached object by pointer address
        obj = _addr2obj[addr]
    except KeyError:
        # create new object and cache it
        cls = classof(cap)
        obj = cls(cap)
        _addr2obj[addr] = obj       # cache object by address
        # set destructor if cls.delete is defined
        if hasattr(cls, '_delete_'):
            _capsule.setDestructor(cap, cls._delete_)
    else:
        assert classof(obj._ptr) is classof(cap)
        # Unset destructor for capsules that are repeated
        _capsule.setDestructor(cap, None)
    return obj


def unwrap(obj):
    '''Unwrap a Wrapper instance into the underlying PyCapsule.
    If `obj` is not a Wrapper instance, returns `obj`.
    '''
    if isinstance(obj, Wrapper):
        return obj._ptr
    else:
        return obj


def register_class(cls):
    clsname = cls.__name__
    _pyclasses['llvm::%s' % clsname] = cls
    return cls


class Wrapper(object):

    __slots__ = '__ptr'

    def __init__(self, ptr):
        _sentry(ptr)
        self.__ptr = ptr

    @property
    def _ptr(self):
        return self.__ptr

    def _release_ownership(self):
        _capsule.setDestructor(self._ptr, None)



