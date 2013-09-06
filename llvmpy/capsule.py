from weakref import WeakKeyDictionary, WeakValueDictionary, ref
from collections import defaultdict
import logging
logger = logging.getLogger(__name__)

NO_DEBUG = False
def silent_logger():
    '''
    Silent logger for unless we have a error message.
    '''
    logger.setLevel(logging.ERROR)
    NO_DEBUG = True

# comment out the line below to re-enable logging at DEBUG level.
silent_logger()

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

def _capsule_weakref_dtor(item):
    addr = item.pointer
    name = item.name
    _addr2refct[addr] -= 1
    refct = _addr2refct[addr]
    assert refct >= 0, "RefCt drop below 0"
    if refct == 0:
        dtor = _addr2dtor.pop((name, addr), None)
        if dtor is not None:
            if not NO_DEBUG:
                # Some globals in logger could be removed by python GC
                # at interpreter teardown.
                # That can cause exception raised and ignored message.
                logger.debug('Destroy %s %s', name, hex(addr))
            dtor(item.capsule)

class Capsule(object):
    "Wraps PyCapsule so that we can build weakref of it."

    from ._capsule import check, getClassName, getName, getPointer

    def __init__(self, capsule):
        assert Capsule.valid(capsule)
        self.capsule = capsule

        weak = WeakRef(self, _capsule_weakref_dtor)
        weak.pointer = self.pointer
        weak.capsule = capsule
        weak.name = self.name
        _capsule2weak[self] = weak
        _addr2refct[self.pointer] += 1

    @property
    def classname(self):
        return self.getClassName(self.capsule)

    @property
    def name(self):
        return self.getName(self.capsule)

    @property
    def pointer(self):
        return self.getPointer(self.capsule)

    @staticmethod
    def valid(capsule):
        return Capsule.check(capsule)

    def get_class(self):
        return _pyclasses[self.classname]

    def instantiate(self):
        cls = self.get_class()
        return cls(self)

    def __eq__(self, other):
        if self.pointer == other.pointer:
            assert self.name == other.name
            return True
        else:
            return False

    def __hash__(self):
        return hash((self.pointer, self.name))

    def __ne__(self, other):
        return not (self == other)

class WeakRef(ref):
    pass

_addr2refct = defaultdict(lambda: 0)
_capsule2weak = WeakKeyDictionary()
_addr2dtor = {}
_pyclasses = {}

# Cache {cls: {addr: obj}}
# NOTE: The same 'addr' may appear in multiple class bins.
_cache = defaultdict(WeakValueDictionary)

def release_ownership(old):
    logger.debug('Release %s', old)
    addr = Capsule.getPointer(old)
    name = Capsule.getName(old)
    if _addr2dtor.get((name, addr)) is None:
        clsname = Capsule.getClassName(old)
        if not _pyclasses[clsname]._has_dtor():
            return
        # Guard duplicated release
        raise Exception("Already released")
    _addr2dtor[(name, addr)] = None


def obtain_ownership(cap):
    cls = cap.get_class()
    if cls._has_dtor():
        addr = cap.pointer
        name = cap.name
        assert _addr2dtor[addr] is None
        _addr2dtor[(name, addr)] = cls._delete_

def has_ownership(cap):
    addr = Capsule.getPointer(cap)
    name = Capsule.getName(cap)
    return _addr2dtor.get((name, addr)) is not None

def wrap(cap, owned=False):
    '''Wrap a PyCapsule with the corresponding Wrapper class.
    If `cap` is not a PyCapsule, returns `cap`
    '''
    if not Capsule.valid(cap):
        if isinstance(cap, list):
            return list(map(wrap, cap))
        return cap     # bypass if cap is not a PyCapsule and not a list

    cap = Capsule(cap)
    cls = cap.get_class()
    addr = cap.pointer
    name = cap.name
    # lookup cached object
    if cls in _cache and addr in _cache[cls]:
        obj = _cache[cls][addr]
    else:
        if not owned and cls._has_dtor():
            _addr2dtor[(name, addr)] = cls._delete_
        obj = cap.instantiate()
        _cache[cls][addr] = obj    # cache it
    return obj

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

    __slots__ = '__capsule'

    def __init__(self, capsule):
        self.__capsule = capsule

    @property
    def _capsule(self):
        return self.__capsule

    @property
    def _ptr(self):
        return self._capsule.capsule

    def __hash__(self):
        return hash(self._capsule)

    def __eq__(self, other):
        return self._capsule == other._capsule

    def __ne__(self, other):
        return not(self == other)

    def _downcast(self, newcls):
        return downcast(self, newcls)

    @classmethod
    def _has_dtor(cls):
        return hasattr(cls, '_delete_')

def downcast(obj, cls):
    from . import _api
    if type(obj) is cls:
        return obj
    fromty = obj._llvm_type_
    toty = cls._llvm_type_
    logger.debug("Downcast %s to %s" , fromty, toty)
    fname = 'downcast_%s_to_%s' % (fromty, toty)
    fname = fname.replace('::', '_')
    if not hasattr(_api.downcast, fname):
        fmt = "Downcast from %s to %s is not supported"
        raise TypeError(fmt % (fromty, toty))
    caster = getattr(_api.downcast, fname)
    old = unwrap(obj)
    new = caster(old)
    used_to_own = has_ownership(old)
    res = wrap(new, owned=not used_to_own)
    if not res:
        raise ValueError("Downcast failed")
    return res

