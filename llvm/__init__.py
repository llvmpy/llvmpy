"""Common classes related to LLVM.

"""

VERSION = '0.3'


#===----------------------------------------------------------------------===
# Exceptions
#===----------------------------------------------------------------------===

class LLVMException(Exception):
    """Generic LLVM exception."""

    def __init__(self, msg=""):
        Exception.__init__(self, msg)


#===----------------------------------------------------------------------===
# Ownables
#===----------------------------------------------------------------------===

class Ownable(object):
    """Objects that can be owned.

    Modules and Module Providers can be owned, i.e., the responsibility of
    destruction of ownable objects can be handed over to other objects. The
    llvm.Ownable class represents objects that can be so owned. This class
    is NOT intended for public use.
    """

    def __init__(self, ptr, del_fn):
        self.ptr = ptr
        self.owner = None
        self.del_fn = del_fn

    def _own(self, owner):
        if self.owner:
            raise LLVMException, "object already owned"
        self.owner = owner

    def _disown(self):
        if not self.owner:
            raise LLVMException, "not owned"
        self.owner = None

    def __del__(self):
        if not self.owner:
            self.del_fn(self.ptr)

