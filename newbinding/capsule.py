from weakref import WeakKeyDictionary, WeakValueDictionary, ref
from collections import defaultdict
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

def _capsule_weakref_dtor(item):
    addr = item.pointer
    _addr2refct[addr] -= 1
    refct = _addr2refct[addr]
    assert refct >= 0, "RefCt drop below 0"
    if refct == 0:
        dtor = _addr2dtor.pop(addr, None)
        if dtor is not None:
            logger.debug('Destroy %s %s', item.name, hex(item.pointer))
            dtor(item.capsule)

class Capsule(object):
    "Wraps PyCapsule so that we can build weakref of it."

    from _capsule import check, getClassName, getName, getPointer
    
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
        return Capsule.getClassName(self.capsule)

    @property
    def name(self):
        return Capsule.getName(self.capsule)

    @property
    def pointer(self):
        return Capsule.getPointer(self.capsule)

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
    if _addr2dtor[addr] is None:
        # Guard deduplicated release
        raise Exception("Already released")
    _addr2dtor[addr] = None


def has_ownership(cap):
    addr = Capsule.getPointer(cap)
    return _addr2dtor.get(addr) is not None

def wrap(cap, owned=False):
    '''Wrap a PyCapsule with the corresponding Wrapper class.
    If `cap` is not a PyCapsule, returns `cap`
    '''
    if not Capsule.valid(cap):
        if isinstance(cap, list):
            return map(wrap, cap)
        return cap     # bypass if cap is not a PyCapsule and not a list

    cap = Capsule(cap)
    cls = cap.get_class()
    addr = cap.pointer
    try: # lookup cached object
        return _cache[cls][addr]
    except KeyError:
        if not owned and hasattr(cls, '_delete_'):
            _addr2dtor[addr] = cls._delete_
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

    def __eq__(self, other):
        return self._capsule == other._capsule

    def __ne__(self, other):
        return self._capsule != other._capsule

    def _downcast(self, newcls):
        return downcast(self, newcls)

def downcast(obj, cls):
    import _api
    if type(obj) is cls:
        return obj
    fromty = obj._llvm_type_
    toty = cls._llvm_type_
    logger.debug("Downcast %s to %s" , fromty, toty)
    fname = 'downcast_%s_to_%s' % (fromty, toty)
    fname = fname.replace('::', '_')
    try:
        caster = getattr(_api, fname)
    except AttributeError:
        fmt = "Downcast from %s to %s is not supported"
        raise TypeError(fmt % (fromty, toty))
    old = unwrap(obj)
    new = caster(old)
    used_to_own = has_ownership(old)
    return wrap(new, owned=not used_to_own)
