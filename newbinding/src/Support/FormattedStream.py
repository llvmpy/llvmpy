from binding import *
from ..namespace import llvm
from raw_ostream import raw_ostream

@llvm.Class(raw_ostream)
class formatted_raw_ostream:
    _include_ = 'llvm/Support/FormattedStream.h'
    new = Constructor(ref(raw_ostream), cast(bool, Bool))

