from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


from llvmpy import extra

version = extra.get_llvm_version()
del extra

class Wrapper(object):
    def __init__(self, ptr):
        assert ptr
        self.__ptr = ptr

    @property
    def _ptr(self):
        try:
            return self.__ptr
        except AttributeError:
            raise AttributeError("_ptr resource has been removed")

    @_ptr.deleter
    def _ptr(self):
        del self.__ptr


def _extract_ptrs(objs):
    return [(x._ptr if x is not None else None)
            for x in objs]

class LLVMException(Exception):
    pass

def test(verbosity=1):
    """test(verbosity=1) -> TextTestResult

        Run self-test, and return the number of failures + errors
        """
    from llvm.tests import run

    result = run(verbosity=verbosity)

    return len(result.failures) + len(result.errors)

