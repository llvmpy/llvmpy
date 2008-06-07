"""Common classes related to LLVM.

"""

#===----------------------------------------------------------------------===
# Exceptions
#===----------------------------------------------------------------------===

class LLVMException(Exception):

    def __init__(self, msg=""):
        Exception.__init__(self, msg)


#===----------------------------------------------------------------------===
# Ownables
#===----------------------------------------------------------------------===

class Ownable(object):

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

