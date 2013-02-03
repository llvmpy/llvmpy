from binding import *
from ..namespace import llvm

@llvm.Class()
class SmallVector_Type:
    _realname_ = 'SmallVector<llvm::Type*,8>'
    delete = Destructor()

@llvm.Class()
class SmallVector_Value:
    _realname_ = 'SmallVector<llvm::Value*,8>'
    delete = Destructor()

@llvm.Class()
class SmallVector_Unsigned:
    _realname_ = 'SmallVector<unsigned,8>'
    delete = Destructor()
