'''
Wrapped the extra functions in _api.so
'''

import capsule
import _api
#
# Re-export the native API from the _api.extra and wrap the functions
#

def _wrapper(func):
    "Wrap the re-exported functions"
    def _core(*args):
        unwrapped = map(capsule.unwrap, args)
        ret = func(*unwrapped)
        return capsule.wrap(ret)
    return _core

def _init(glob):
    for k, v in _api.extra.__dict__.items():
        glob[k] = _wrapper(v)

_init(globals())

#
# Downcasts
#

def downcast(obj, cls):
    if type(obj) is cls:
        return obj
    fromty = obj._llvm_type_
    toty = cls._llvm_type_
    fname = 'downcast_%s_to_%s' % (fromty, toty)
    fname = fname.replace('::', '_')
    try:
        caster = getattr(_api, fname)
    except AttributeError:
        fmt = "Downcast from %s to %s is not supported"
        raise TypeError(fmt % (fromty, toty))
    old = capsule.unwrap(obj)
    new = caster(old)
    return capsule.downcast(old, new)