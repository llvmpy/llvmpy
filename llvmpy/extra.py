'''
Wrapped the extra functions in _api.so
'''

from llvmpy import capsule
from llvmpy import _api
#
# Re-export the native API from the _api.extra and wrap the functions
#

def _wrapper(func):
    "Wrap the re-exported functions"
    def _core(*args):
        unwrapped = list(map(capsule.unwrap, args))
        ret = func(*unwrapped)
        return capsule.wrap(ret)
    return _core

def _init(glob):
    for k, v in _api.extra.__dict__.items():
        glob[k] = _wrapper(v)

_init(globals())


