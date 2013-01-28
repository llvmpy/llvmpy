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
    __slots__ = 'capsule', 'dtor', 'owning'

_pyclasses = {}
_addr2obj = WeakValueDictionary()
_owners = {}

def _sentry(ptr):
    assert _capsule.check(ptr)

def classof(cap):
    cls = _capsule.getClassName(cap)
    return _pyclasses[cls]

def _capsule_destructor(weak):
    if weak.owning:
        cap = weak.capsule
        addr = _capsule.getPointer(cap)
        cls = _capsule.getClassName(cap)
        logger.debug("destroy pointer 0x%08X to %s", addr, cls)
        weak.dtor(cap)
        del _owners[addr]

def release_ownership(old):
    addr = _capsule.getPointer(old)
    if hasattr(old, '_delete_'):
        oldweak = _owners[addr]
        oldweak.owning = False # dis-own
        del _owners[addr]

def wrap(cap):
    '''Wrap a PyCapsule with the corresponding Wrapper class.
    If `cap` is not a PyCapsule, returns `cap`
    '''
    if not _capsule.check(cap):
        if isinstance(cap, list):
            return map(wrap, cap)
        return cap     # bypass if cap is not a PyCapsule and not a list
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
            weak.owning = True
            weak.dtor = cls._delete_
    else:
        oldcls = classof(obj._ptr)
        newcls = classof(cap)
        if issubclass(oldcls, newcls):
            # do auto downcast
            pass
        else:
            assert oldcls is newcls, (cap, obj, oldcls, newcls)
    return obj

def downcast(old, new):
    assert old is not new
    oldcls = classof(old)
    newcls = classof(new)
    assert issubclass(newcls, oldcls)
    release_ownership(old)
    del _addr2obj[_capsule.getPointer(old)] # clear cache
    return wrap(new)

def unwrap(obj):
    '''Unwrap a Wrapper instance into the underlying PyCapsule.
    If `obj` is not a Wrapper instance, returns `obj`.
    '''
    if isinstance(obj, Wrapper):
        return obj._ptr
    else:
        return obj


def register_class(clsname):
    def _wrapped(cls):
        _pyclasses[clsname] = cls
        return cls
    return _wrapped


class Wrapper(object):

    __slots__ = '__ptr'

    def __init__(self, ptr):
        _sentry(ptr)
        self.__ptr = ptr

    @property
    def _ptr(self):
        return self.__ptr

