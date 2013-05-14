from binding import *
from .Value import ValueSymbolTable, Value
from .ADT.StringRef import StringRef

@ValueSymbolTable
class ValueSymbolTable:
    new = Constructor()
    delete = Destructor()
    lookup = Method(ptr(Value), cast(str, StringRef))
    empty = Method(cast(Bool, bool))
    size = Method(cast(Unsigned, int))
    dump = Method(Void)

