from binding import *
from .Value import ValueSymbolTable, Value
from .ADT.StringRef import StringRef

@ValueSymbolTable
class ValueSymbolTable:
    if LLVM_VERSION >= (3, 3):
        _include_ = 'llvm/IR/ValueSymbolTable.h'
    else:
        _include_ = 'llvm/ValueSymbolTable.h'
    new = Constructor()
    delete = Destructor()
    lookup = Method(ptr(Value), cast(str, StringRef))
    empty = Method(cast(Bool, bool))
    size = Method(cast(Unsigned, int))
    dump = Method(Void)

