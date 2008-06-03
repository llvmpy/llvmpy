"""Common classes related to LLVM.

"""

#===----------------------------------------------------------------------===
# Exceptions
#===----------------------------------------------------------------------===

class LLVMException(Exception):

    def __init__(self, msg=""):
        Exception.__init__(self, msg)


