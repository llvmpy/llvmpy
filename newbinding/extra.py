'''
Wrapped the extra functions in _api.so
'''

import capsule

def _wrapper(func):
    def _core(*args):
        unwrapped = map(capsule.unwrap, args)
        ret = func(*unwrapped)
        return capsule.wrap(ret)
    return _core

def _init(glob):
    from _api import extra
    for k, v in extra.__dict__.items():
        glob[k] = _wrapper(v)

_init(globals())

