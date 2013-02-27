from binding import *
from .namespace import llvm
from .Value import Value, User

@User
class User:
    _downcast_ = Value
    getOperand = Method(ptr(Value), cast(int, Unsigned))
    setOperand = Method(Void, cast(int, Unsigned), ptr(Value))
    getNumOperands = Method(cast(Unsigned, int))

