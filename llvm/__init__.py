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
        return self.__ptr


def _extract_ptrs(objs):
    return [(x._ptr if x is not None else None)
            for x in objs]

class LLVMException(Exception):
    pass

def test(verbosity=1):
    """test(verbosity=1) -> TextTestResult

        Run self-test, and return unittest.runner.TextTestResult object.
        """
    from llvm.test_llvmpy import run

    return run(verbosity=verbosity)

