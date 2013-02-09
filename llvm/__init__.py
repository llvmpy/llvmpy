class Wrapper(object):
    def __init__(self, ptr):
        self.__ptr = ptr

    @property
    def _ptr(self):
        return self.__ptr


def _extract_ptrs(objs):
    return [x._ptr for x in objs]
