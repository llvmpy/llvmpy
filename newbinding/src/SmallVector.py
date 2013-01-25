from binding import *
from namespace import llvm

@llvm.Class()
class SmallVector_Type:
    delete = Destructor()
