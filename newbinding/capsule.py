import _capsule
from weakref import WeakValueDictionary, ref
import logging
logger = logging.getLogger(__name__)

def set_debug(enabled):
    '''
    Side-effect: configure logger with it is not configured.
    '''
    if enabled:
        # If no handlers are configured for the root logger,
        # build a default handler for debugging.
        # Can we do better?
        if not logger.root.handlers:
            logging.basicConfig()
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.WARNING)


class WeakRef(ref):
    __slots__ = 'capsule', 'dtor'

_pyclasses = {}
_addr2obj = WeakValueDictionary()
_owners = {}

def _sentry(ptr):
    assert _capsule.check(ptr)

def classof(cap):
    cls = _capsule.getClassName(cap)
    return _pyclasses[cls]

def _capsule_destructor(weak):
    cap = weak.capsule
    addr = _capsule.getPointer(cap)
    cls = _capsule.getClassName(cap)
    logger.debug("destroy pointer %s to %s", addr, cls)
    weak.dtor(cap)
    del _owners[addr]

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
        # set ownership if *cls* defines *_delete_*
        if hasattr(cls, '_delete_'):
            weak = WeakRef(obj, _capsule_destructor)
            _owners[addr] = weak
            weak.capsule = cap
            weak.dtor = cls._delete_
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



